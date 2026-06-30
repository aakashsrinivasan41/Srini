"""Score each Job 0-100 against profile.yaml.

Components (each 0-1, combined by configured weights):
  role         title matches your include list (and isn't excluded)
  location     best matching location tier, or remote signal
  comp         stated comp vs your per-location floor
  arrangement  remote / hybrid / onsite preference (+ onsite comp gate)
  company      flat boost if it's a favorite company
"""
from __future__ import annotations

from .models import Job, normalize_loc
from .experience import fit as experience_fit


def _contains_any(text: str, needles: list[str]) -> str | None:
    t = text.lower()
    for n in needles:
        n = (n or "").strip().lower()
        if n and n in t:
            return n
    return None


def _role_component(job: Job, p: dict) -> tuple[float, str]:
    roles = p["roles"]
    title = job.title.lower()
    if _contains_any(title, roles.get("exclude", [])):
        return 0.0, "excluded title"
    hit = _contains_any(title, roles.get("include", []))
    if hit:
        return 1.0, f"role match: '{hit}'"
    # soft credit: description mentions a target role even if title doesn't
    if job.description and _contains_any(job.description[:1500], roles.get("include", [])):
        return 0.45, "role in description only"
    return 0.15, "weak role match"


def _location_component(job: Job, p: dict) -> tuple[float, str]:
    loc = normalize_loc(job.location)
    locs = p["locations"]
    best = 0.0
    label = "no location tier"
    for tier in locs["tiers"]:
        w = tier["weight"]
        for m in tier["match"]:
            if m == "*":
                if w > best:
                    best, label = w, "fallback tier"
            elif m.lower() in loc:
                if w > best:
                    best, label = w, f"location: '{m}'"
    if job.remote:
        rw = locs.get("remote_weight", 0.85)
        if rw > best:
            best, label = rw, "remote"
    return best, label


def _comp_floor(job: Job, p: dict) -> int:
    loc = normalize_loc(job.location)
    floors = p["compensation"]["min_by_location"]
    if any(x in loc for x in ("new york", "nyc", "manhattan", "brooklyn")):
        return floors["new_york"]
    if any(x in loc for x in ("san francisco", "bay area", "san mateo", "peninsula",
                              "palo alto", "oakland", "san jose")):
        return floors["sf_bay"]
    return floors["other"]


def _comp_component(job: Job, p: dict) -> tuple[float, str]:
    if not job.comp_min:
        return 0.6, "comp not stated"  # neutral-ish, don't punish silence
    floor = _comp_floor(job, p)
    midpoint = (job.comp_min + (job.comp_max or job.comp_min)) / 2
    if midpoint >= floor:
        # reward generously above floor, capped
        return min(1.0, 0.7 + (midpoint - floor) / floor), f"${int(midpoint/1000)}k ≥ floor ${int(floor/1000)}k"
    ratio = midpoint / floor
    return max(0.0, ratio * 0.7), f"${int(midpoint/1000)}k < floor ${int(floor/1000)}k"


def _arrangement_component(job: Job, p: dict) -> tuple[float, str, bool]:
    arr = p["arrangement"]
    loc = normalize_loc(job.location)
    if job.remote:
        return arr["remote"], "remote", False
    if "hybrid" in loc or "hybrid" in (job.employment_type or "").lower():
        return arr["hybrid"], "hybrid", False
    # treat as onsite -> apply comp gate
    onsite_floor = p["compensation"]["onsite_floor"]
    mid = ((job.comp_min or 0) + (job.comp_max or job.comp_min or 0)) / 2
    gated = bool(job.comp_min) and mid < onsite_floor
    return arr["onsite"], "onsite", gated


def _company_component(job: Job, p: dict) -> tuple[float, str]:
    fav = _contains_any(job.company, p.get("favorite_companies", []))
    return (1.0, f"favorite: {fav}") if fav else (0.0, "")


def score_job(job: Job, p: dict) -> Job:
    w = p["weights"]
    r, r_why = _role_component(job, p)
    l, l_why = _location_component(job, p)
    c, c_why = _comp_component(job, p)
    a, a_why, onsite_gated = _arrangement_component(job, p)

    if r == 0.0:  # excluded title -> hard zero
        job.score = 0.0
        job.score_breakdown = {"verdict": r_why}
        return job

    comp_score, comp_why = _company_component(job, p)
    total = (w["role"] * r + w["location"] * l + w["comp"] * c +
             w["arrangement"] * a + w["company"] * comp_score)

    # onsite-below-floor is a near-disqualifier per your rules
    if onsite_gated:
        total *= 0.4
        a_why += " (below onsite comp floor)"

    # ROLE GATE: a job that doesn't actually match a target role must not be
    # rescued by comp/location/remote. Title match = full; description-only =
    # discounted; no real match = crushed below the cutoff.
    if r >= 0.9:
        role_gate, gate_why = 1.0, ""
    elif r >= 0.4:                       # matched only in the description
        role_gate, gate_why = 0.7, " (role only in description)"
    else:                                # weak/no role match
        role_gate, gate_why = 0.22, " (off-target role)"
    total *= role_gate
    r_why += gate_why

    # COMP GATE: stated pay clearly below your floor for that location is a
    # near-disqualifier (e.g. an $85k role in NYC where your floor is $125k).
    # Unknown comp is NOT gated — many strong roles just don't post a number.
    if job.comp_min:
        floor = _comp_floor(job, p)
        mid = (job.comp_min + (job.comp_max or job.comp_min)) / 2
        ratio = (mid / floor) if floor else 1.0
        if ratio < 0.8:
            comp_gate = 0.40
        elif ratio < 0.9:
            comp_gate = 0.65
        elif ratio < 1.0:
            comp_gate = 0.85
        else:
            comp_gate = 1.0
        total *= comp_gate
        if comp_gate < 1.0:
            c_why += f" — GATED ${int(mid/1000)}k < floor ${int(floor/1000)}k"

    # experience-fit guardrail: kill 4y+/quant/senior-eng/manager, nudge early-career
    exp_mult, exp_why = experience_fit(job.description, job.title, p)
    total *= exp_mult

    job.score = round(min(total, 1.0) * 100, 1)
    job.score_breakdown = {
        "role": f"{r:.2f} — {r_why}",
        "location": f"{l:.2f} — {l_why}",
        "comp": f"{c:.2f} — {c_why}",
        "arrangement": f"{a:.2f} — {a_why}",
        "company": f"{comp_score:.2f} — {comp_why}" if comp_why else "0.00",
        "experience": f"×{exp_mult:.2f} — {exp_why}",
    }
    return job


def rank(jobs: list[Job], p: dict) -> list[Job]:
    scored = [score_job(j, p) for j in jobs]
    scored.sort(key=lambda j: j.score, reverse=True)
    return scored


def shortlist(jobs: list[Job], p: dict) -> list[Job]:
    threshold = p.get("shortlist_threshold", 55)
    return [j for j in rank(jobs, p) if j.score >= threshold]
