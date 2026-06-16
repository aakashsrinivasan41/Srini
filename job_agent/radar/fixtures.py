"""Realistic sample API payloads (shaped exactly like the real endpoints) used
by the self-test and the offline `demo` command. No network required."""
from __future__ import annotations

from typing import List

from .models import Job
from .sources import ashby, greenhouse, lever, remotive

GREENHOUSE_PAYLOAD = {
    "jobs": [
        {"id": 101, "title": "Investment Analytics Analyst",
         "location": {"name": "New York, NY"}, "absolute_url": "https://ex.com/gh/101",
         "updated_at": "2026-06-10T00:00:00Z",
         "content": "Support portfolio analytics across funds. 1-3 years of experience. Compensation: $95,000-$120,000."},
        {"id": 102, "title": "Senior Data Analyst",
         "location": {"name": "New York, NY"}, "absolute_url": "https://ex.com/gh/102",
         "content": "Lead analytics. Requires 5+ years of experience."},
        {"id": 103, "title": "Account Manager",
         "location": {"name": "New York, NY"}, "absolute_url": "https://ex.com/gh/103",
         "content": "Own client relationships and renewals."},
        {"id": 104, "title": "Barista",
         "location": {"name": "New York, NY"}, "absolute_url": "https://ex.com/gh/104",
         "content": "Make great coffee."},
        {"id": 105, "title": "Portfolio Analytics Analyst",
         "location": {"name": "New York, NY"}, "absolute_url": "https://ex.com/gh/105",
         "content": "This role requires 6+ years of experience in risk."},
    ]
}

LEVER_PAYLOAD = [
    {"id": "L1", "text": "Associate Product Manager",
     "categories": {"location": "San Francisco, CA"}, "hostedUrl": "https://ex.com/lv/apm",
     "descriptionPlain": "Work with data teams. 0-2 years of experience."},
    {"id": "L2", "text": "Data Analyst",
     "categories": {"location": "Remote - US"}, "hostedUrl": "https://ex.com/lv/da",
     "descriptionPlain": "SQL and dashboards. Pay range $70,000 - $90,000."},
    {"id": "L3", "text": "Customer Success Manager",
     "categories": {"location": "Remote"}, "hostedUrl": "https://ex.com/lv/csm",
     "descriptionPlain": "Drive adoption and retention."},
]

ASHBY_PAYLOAD = {
    "jobs": [
        {"id": "A1", "title": "Quantitative Analyst", "location": "New York", "isListed": True,
         "isRemote": False, "jobUrl": "https://ex.com/ash/q",
         "compensation": {"compensationTierSummary": "$120K – $150K"},
         "descriptionPlain": "Build models. 2 years of experience preferred."},
        {"id": "A2", "title": "Solutions Consultant", "location": "San Francisco", "isListed": True,
         "jobUrl": "https://ex.com/ash/sc",
         "compensation": {"compensationTierSummary": "$90K – $130K"},
         "descriptionPlain": "Client-facing technical role. 1+ years of experience."},
        {"id": "A3", "title": "Investment Operations Analyst", "location": "Austin, TX", "isListed": True,
         "jobUrl": "https://ex.com/ash/io",
         "descriptionPlain": "Trade settlement and reconciliation."},
        {"id": "A4", "title": "Lead Data Scientist", "location": "San Francisco, CA", "isListed": True,
         "jobUrl": "https://ex.com/ash/lds",
         "descriptionPlain": "Lead a team of scientists."},
    ]
}

REMOTIVE_PAYLOAD = {
    "jobs": [
        {"id": 9001, "title": "Financial Analyst", "company_name": "Acme",
         "candidate_required_location": "USA", "salary": "$60,000 - $75,000",
         "url": "https://ex.com/rm/fa", "description": "FP&A and reporting."},
        {"id": 9002, "title": "Business Analyst", "company_name": "Globex",
         "candidate_required_location": "Worldwide", "salary": "",
         "url": "https://ex.com/rm/ba", "description": "Requirements gathering. 2 years of experience."},
    ]
}


# A realistic slice of LinkedIn's public guest-endpoint HTML (two job cards).
LINKEDIN_HTML = """
<ul class="jobs-search__results-list">
  <li>
    <div class="base-card" data-entity-urn="urn:li:jobPosting:3811111111">
      <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/data-analyst-at-lever-co-3811111111?refId=xyz"></a>
      <div class="base-search-card__info">
        <h3 class="base-search-card__title">Data Analyst</h3>
        <h4 class="base-search-card__subtitle"><a class="hidden-nested-link" href="/company/lever">Lever Co</a></h4>
        <span class="job-search-card__location">New York, NY</span>
        <time class="job-search-card__listdate" datetime="2026-06-12">2 days ago</time>
      </div>
    </div>
  </li>
  <li>
    <div class="base-card" data-entity-urn="urn:li:jobPosting:3822222222">
      <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/risk-analyst-at-bigbank-3822222222?refId=abc"></a>
      <div class="base-search-card__info">
        <h3 class="base-search-card__title">Risk Analyst</h3>
        <h4 class="base-search-card__subtitle"><a class="hidden-nested-link" href="/company/bigbank">BigBank</a></h4>
        <span class="job-search-card__location">New York, NY</span>
        <time class="job-search-card__listdate" datetime="2026-06-13">1 day ago</time>
      </div>
    </div>
  </li>
</ul>
"""


def demo_jobs() -> List[Job]:
    return (
        greenhouse.parse(GREENHOUSE_PAYLOAD, "Greenhouse Co")
        + lever.parse(LEVER_PAYLOAD, "Lever Co")
        + ashby.parse(ASHBY_PAYLOAD, "Ashby Co")
        + remotive.parse(REMOTIVE_PAYLOAD)
    )
