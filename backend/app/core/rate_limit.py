from fastapi import Request
from redis.asyncio import Redis, from_url

from app.core.config import get_settings
from app.core.exceptions import RateLimitError

settings = get_settings()


def get_redis() -> Redis:
    # Not cached: a module-level client would bind its connection pool to
    # whatever asyncio event loop was running at first use, which breaks
    # under test runners that open a fresh loop per test.
    return from_url(settings.redis_url, decode_responses=True)


def rate_limiter(key_prefix: str, max_requests: int, window_seconds: int):
    """Fixed-window rate limit keyed by client IP, backed by Redis.

    Applied to /auth/* endpoints to blunt brute-force and OTP-spam attempts —
    the per-account lockout in AuthService handles the rest.
    """

    async def _check(request: Request) -> None:
        client_host = request.client.host if request.client else "unknown"
        key = f"ratelimit:{key_prefix}:{client_host}"
        redis = get_redis()
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window_seconds)
        if current > max_requests:
            raise RateLimitError("Trop de tentatives, réessayez plus tard")

    return _check
