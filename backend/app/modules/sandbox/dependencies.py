from app.core.config import get_settings
from app.core.exceptions import NotFoundError

settings = get_settings()


def require_sandbox_mode() -> None:
    """Sandbox-only endpoints must not exist in production — a 404 hides
    them exactly like a route that was never registered."""
    if not settings.sandbox_mode:
        raise NotFoundError("Not found")
