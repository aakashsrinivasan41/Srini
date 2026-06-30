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
    """Primary roles (your focus) score full; secondary (CS/impl/sol-eng) score
    lower so they only surface when strong on everything else."""
    roles = p["roles"]
    title = job.title.lower()
    if _contains_any(title, roles.get("exclude", [])):
        return 0.0, "excluded title"
    hit = _contains_any(title, roles.get("primary", []))
    if hit:
        return 1.0, f"primary: '{hit}'"
    hit = _contains_any(title, roles.get("secondary", []))
    if hit:
        return 0.6, f"secondary: '{hit}' (not your focus)"
    desc = job.description[:1500] if job.description else ""
    if desc:
        hp = _contains_any(desc, roles.get("primary", []))
        if hp:
            return 0.5, f"primary in description: '{hp}'"
        if _contains_any(desc, roles.get("secondary", [])):
            return 0.32, "secondary in description"
    return 0.12, "off-target role"


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

    # (The old onsite-comp gate was removed — it double-penalized the onsite
    #  bank/fund-ops roles you actually want. Onsite is already reflected in the
    #  arrangement component, and underpay is handled by the comp gate below.)
    _ = onsite_gated  # kept for breakdown wording only

    # ROLE GATE: an off-target role must not be rescued by comp/location/remote.
    # Primary/secondary tiers already differ in role weight; here we only crush
    # the genuinely off-target tail so it falls below the cutoff.
    if r < 0.25:
        total *= 0.22
        r_why += " (off-target)"

    # SENIORITY PENALTY: you're ~2 yrs, so over-level titles (Senior/Lead/
    # Manager/level II+) get knocked down even with no description to read.
    if _contains_any(job.title.lower(), p["roles"].get("senior_penalty_terms", [])):
        total *= 0.5
        r_why += " [senior-title penalty]"

    # COMP GATE: penalize only CLEARLY-underpaid roles (e.g. an $85k media job in
    # NYC), while letting realistic bank/fund-ops pay (~$95-120k) through. Tuned
    # so ratio<0.8 sinks below the cutoff but 0.8-0.95 is only a soft nudge.
    # Unknown comp is NOT gated — many strong roles just don't post a number.
    if job.comp_min:
        floor = _comp_floor(job, p)
        mid = (job.comp_min + (job.comp_max or job.comp_min)) / 2
        ratio = (mid / floor) if floor else 1.0
        if ratio < 0.8:
            comp_gate = 0.50
        elif ratio < 0.95:
            comp_gate = 0.80
        else:
            comp_gate = 1.0
        total *= comp_gate
        if comp_gate < 1.0:
            c_why += f" — low vs floor ${int(floor/1000)}k"

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
