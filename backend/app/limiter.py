"""
Rate limiter configuration shared across API routers and application entry point.
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_client_ip(request):
    """
    Extracts the true client IP address.
    If TRUST_PROXY is enabled, extracts the client IP from X-Forwarded-For.
    Otherwise falls back to the direct socket address.
    """
    if os.getenv("TRUST_PROXY", "false").lower() in ("1", "true", "yes"):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=get_client_ip)

