"""Source adapters. Each module exposes:
    parse(payload, company) -> list[Job]   (pure, testable)
    fetch(**cfg)            -> list[Job]    (network)
"""
from . import ashby, greenhouse, lever, linkedin, remotive  # noqa: F401
