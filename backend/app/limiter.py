"""
Rate limiter configuration shared across API routers and application entry point.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
