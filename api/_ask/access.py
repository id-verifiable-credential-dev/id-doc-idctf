"""Who may call the function, and how often.

The limiter lives in the memory of one warm instance, so it is a brake and
not a wall (spec G7). The real cap is the quota on the key in Google AI
Studio.
"""

from __future__ import annotations

import ipaddress
from collections import deque
from urllib.parse import urlparse


class Limiter:
    def __init__(self, limit: int, window: float) -> None:
        self.limit = limit
        self.window = window
        self._hits: dict[str, deque[float]] = {}

    def allow(self, key: str, now: float) -> bool:
        hits = self._hits.setdefault(key, deque())
        while hits and now - hits[0] >= self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        return True


_LOCAL_HOSTS = {"localhost", "127.0.0.1"}


def origin_allowed(origin: str | None, host: str | None, vercel_env: str | None) -> bool:
    """Same-origin only. Outside Vercel, and under `vercel dev` (VERCEL_ENV=development)
    on a linked project, localhost and a missing header pass."""
    if not vercel_env or vercel_env == "development":
        if not origin:
            return True
        parsed = urlparse(origin)
        return parsed.hostname in _LOCAL_HOSTS
    if not origin or not host:
        return False
    parsed = urlparse(origin)
    return parsed.scheme == "https" and parsed.netloc.lower() == host.lower()


def _canonical_ip(candidate: str) -> str | None:
    """Parse candidate as an IP address and return its canonical form, or None.

    A bare parse is not enough: ipaddress.ip_address accepts an IPv6 zone id
    (`2001:db8::1%eth0`) and keeps it in str(), so returning the raw header
    text would let a caller mint a fresh rate-limit key per request just by
    varying the zone. Strip the zone and re-parse to get a stable key.
    """
    try:
        addr = ipaddress.ip_address(candidate)
    except ValueError:
        return None
    if getattr(addr, "scope_id", None):
        try:
            addr = ipaddress.ip_address(candidate.split("%", 1)[0])
        except ValueError:
            return None
    return str(addr)


def client_key(headers: dict[str, str]) -> str:
    lower = {k.lower(): v for k, v in headers.items()}
    real = lower.get("x-real-ip", "").strip()
    if real:
        canonical = _canonical_ip(real)
        if canonical:
            return canonical
    forwarded = lower.get("x-forwarded-for", "")
    first = forwarded.split(",")[0].strip()
    if first:
        canonical = _canonical_ip(first)
        if canonical:
            return canonical
    return "unknown"
