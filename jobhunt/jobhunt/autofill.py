"""Browser autofill assistant for application forms (review-before-submit).

Design principles, deliberately:
  * Opens a REAL visible browser you control — nothing happens headless.
  * Fills standard fields from profile.yaml + uploads your resume.
  * NEVER clicks the final submit button unless you pass submit=True AND
    confirm at the prompt. Default is to fill, then hand the tab to you.
  * Matches fields by their visible label text, so it works across Greenhouse,
    Lever, and Ashby hosted forms without per-site selectors.

This keeps you compliant with ATS terms (which generally forbid automated
submission) and prevents an unrecoverable mistake on a real application.

Setup:  pip install playwright && playwright install chromium
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Optional

from .models import load_profile

# label-substring -> profile value resolver
def _field_map(p: dict) -> dict[str, str]:
    i = p["identity"]
    return {
        "first name": i["first_name"],
        "last name": i["last_name"],
        "full name": i["full_name"],
        "preferred name": i["first_name"],
        "email": i["email"],
        "phone": i["phone"],
        "linkedin": i["linkedin"],
        "github": i.get("github", ""),
        "website": i.get("website", ""),
        "portfolio": i.get("website", ""),
        "city": i["location_city"],
        "state": i["location_state"],
        "location": f"{i['location_city']}, {i['location_state']}",
        "address": i.get("address", ""),
    }


def autofill(url: str, *, submit: bool = False, answers: Optional[dict] = None,
             pause_seconds: int = 0) -> None:
    """Open `url`, fill known fields, optionally pre-fill drafted `answers`
    ({question_substring: text}), then wait for you.

    submit=False (default): fills and hands control to you — you review & click.
    submit=True: still asks for an explicit y/N at the terminal first.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("pip install playwright && playwright install chromium")

    p = load_profile()
    fmap = _field_map(p)
    resume = Path(p.get("resume_path", "")).expanduser()
    answers = answers or {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        print(f"→ Opening {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(2)

        filled, skipped = [], []

        # 1) text-like inputs + textareas, matched by associated label text
        for el in page.query_selector_all("input, textarea"):
            try:
                itype = (el.get_attribute("type") or "text").lower()
                if itype in ("hidden", "submit", "button", "checkbox", "radio", "file"):
                    continue
                label = _label_for(page, el)
                if not label:
                    continue
                value = _resolve(label, fmap, answers)
                if value:
                    el.fill(value)
                    filled.append(f"{label.strip()[:40]} = {value[:40]}")
            except Exception as e:  # noqa: BLE001
                skipped.append(f"{label if 'label' in dir() else '?'}: {e}")

        # 2) resume upload
        if resume.exists():
            for fin in page.query_selector_all('input[type="file"]'):
                try:
                    fin.set_input_files(str(resume))
                    filled.append(f"resume uploaded: {resume.name}")
                    break
                except Exception:  # noqa: BLE001
                    pass
        else:
            skipped.append(f"resume not found at {resume}")

        print("\nFilled:")
        for f in filled:
            print(f"  ✓ {f}")
        if skipped:
            print("Needs your attention:")
            for s in skipped:
                print(f"  • {s}")

        print("\n" + "=" * 60)
        print("Fields are pre-filled. Review EVERYTHING in the browser:")
        print("  - dropdowns (work auth, sponsorship, EEO) are intentionally left to you")
        print("  - verify drafted answers read correctly")
        if submit:
            ans = input("Type 'submit' to click the submit button, anything else to skip: ")
            if ans.strip().lower() == "submit":
                _click_submit(page)
                print("Submitted.")
            else:
                print("Skipped auto-submit. Submit manually if you want to.")
        else:
            input("Review, then submit yourself in the browser. Press Enter here to close...")

        if pause_seconds:
            time.sleep(pause_seconds)
        browser.close()


def _label_for(page, el) -> str:
    """Best-effort visible label for an input."""
    # explicit <label for=id>
    eid = el.get_attribute("id")
    if eid:
        lab = page.query_selector(f'label[for="{eid}"]')
        if lab:
            return (lab.inner_text() or "").lower()
    # aria-label / placeholder / name
    for attr in ("aria-label", "placeholder", "name"):
        v = el.get_attribute(attr)
        if v:
            return v.lower()
    return ""


def _resolve(label: str, fmap: dict, answers: dict) -> str:
    label = label.lower()
    # drafted free-text answers take priority on long questions
    for q, text in answers.items():
        if q.lower() in label:
            return text
    for key, val in fmap.items():
        if key in label and val:
            return val
    return ""


def _click_submit(page) -> None:
    for sel in ('button[type="submit"]', 'input[type="submit"]',
                'button:has-text("Submit")', 'button:has-text("Apply")'):
        btn = page.query_selector(sel)
        if btn:
            btn.click()
            time.sleep(3)
            return
    print("Could not locate a submit button — submit manually.")
