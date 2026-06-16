"""Job Radar — a personal, profile-driven job search scanner.

Scans friendly job-board APIs (Greenhouse, Lever, Ashby, Remotive), scores the
results against your profile (target roles, keywords, location, salary,
experience), de-duplicates and tracks them over time, and produces a ranked
CLI summary + a self-contained HTML dashboard.

Everything is driven by `profile.yaml` and `config/sources.yaml`, so handing the
tool to someone in a different field is just a matter of swapping those files.
"""

__version__ = "1.0.0"
