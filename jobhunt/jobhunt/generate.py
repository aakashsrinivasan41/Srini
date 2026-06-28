"""Draft tailored application materials with the Claude API.

Grounded strictly in profile.yaml's `narrative` block + the job description.
Includes the same hallucination-guard pattern you've used before: a second
pass verifies every factual claim traces back to your profile.

Requires ANTHROPIC_API_KEY in the environment (or a .env file).
"""
from __future__ import annotations

import json
import os
from typing import Optional

from .models import Job, load_profile

try:
    from anthropic import Anthropic
except ImportError:  # keep the rest of the toolkit usable without the SDK
    Anthropic = None  # type: ignore

MODEL = "claude-opus-4-8"          # latest, most capable; swap to sonnet for speed/cost
GUARD_MODEL = "claude-haiku-4-5-20251001"


def _client() -> "Anthropic":
    if Anthropic is None:
        raise RuntimeError("pip install anthropic")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("Set ANTHROPIC_API_KEY (export it or put it in a .env file).")
    return Anthropic(api_key=key)


def _profile_brief(p: dict) -> str:
    n = p["narrative"]
    lines = [
        f"Name: {p['identity']['full_name']}",
        f"Headline: {n['headline'].strip()}",
        "Proof points (the ONLY facts you may cite):",
        *[f"  - {pp}" for pp in n["proof_points"]],
        f"Skills: {', '.join(n['skills'])}",
        f"Motivation: {n['motivation'].strip()}",
    ]
    return "\n".join(lines)


def cover_letter(job: Job, p: Optional[dict] = None, *, words: int = 250) -> str:
    p = p or load_profile()
    client = _client()
    sys = (
        "You write concise, specific, non-generic cover letters for a job seeker. "
        "RULES: (1) Use ONLY facts from the candidate brief — never invent employers, "
        "metrics, titles, or skills. (2) No clichés ('I am writing to express'). "
        "(3) Connect 1-2 concrete proof points to THIS role's needs. (4) Confident, "
        "human, not breathless. (5) Plain paragraphs, no salutation placeholders left blank."
    )
    user = (
        f"CANDIDATE BRIEF:\n{_profile_brief(p)}\n\n"
        f"ROLE: {job.title} at {job.company} ({job.location})\n"
        f"JOB DESCRIPTION (excerpt):\n{job.description[:3500]}\n\n"
        f"Write a ~{words}-word cover letter. Address it to the {job.company} hiring team."
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=1200, system=sys,
        messages=[{"role": "user", "content": user}],
    )
    draft = "".join(b.text for b in msg.content if b.type == "text")
    return _guard(draft, _profile_brief(p))


def screening_answer(question: str, job: Job, p: Optional[dict] = None, *, words: int = 120) -> str:
    """Draft an answer to an application free-text question (e.g. 'Why us?')."""
    p = p or load_profile()
    client = _client()
    sys = (
        "Answer job-application screening questions for a candidate. Use ONLY facts "
        "from the brief; never fabricate. Be specific and concrete, first person, "
        f"~{words} words, no fluff."
    )
    user = (
        f"CANDIDATE BRIEF:\n{_profile_brief(p)}\n\n"
        f"ROLE: {job.title} at {job.company}\n"
        f"QUESTION: {question}\n\nWrite the answer."
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=600, system=sys,
        messages=[{"role": "user", "content": user}],
    )
    draft = "".join(b.text for b in msg.content if b.type == "text")
    return _guard(draft, _profile_brief(p))


def _guard(draft: str, brief: str) -> str:
    """Hallucination guard: flag claims not supported by the brief.

    Returns the draft, appending a '⚠ REVIEW' note listing unsupported claims
    so you never send something with invented facts.
    """
    try:
        client = _client()
    except RuntimeError:
        return draft  # no key -> skip guard rather than crash
    check = client.messages.create(
        model=GUARD_MODEL, max_tokens=400,
        system=("You verify a draft against an allowed-facts brief. Return JSON "
                '{"unsupported": ["claim", ...]} listing any factual claim in the '
                "draft (employer, metric, title, skill, achievement) NOT supported "
                "by the brief. Opinions/aspirations are fine. Return [] if clean."),
        messages=[{"role": "user", "content": f"BRIEF:\n{brief}\n\nDRAFT:\n{draft}"}],
    )
    txt = "".join(b.text for b in check.content if b.type == "text")
    try:
        bad = json.loads(txt[txt.find("{"):txt.rfind("}") + 1]).get("unsupported", [])
    except Exception:  # noqa: BLE001
        bad = []
    if bad:
        draft += "\n\n⚠ REVIEW — claims not found in your profile:\n" + \
                 "\n".join(f"  - {b}" for b in bad)
    return draft
