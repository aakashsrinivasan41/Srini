"""Source adapters: each turns one company's ATS board into a list[Job]."""
from .greenhouse import fetch as greenhouse_fetch
from .lever import fetch as lever_fetch
from .ashby import fetch as ashby_fetch

FETCHERS = {
    "greenhouse": greenhouse_fetch,
    "lever": lever_fetch,
    "ashby": ashby_fetch,
}
