from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title="NasrCash API",
    description="Wallet local et cartes virtuelles internationales — MVP sandbox (Guinée / GNF)",
    version="0.1.0",
)

register_exception_handlers(app)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {
        "status": "ok",
        "environment": settings.environment,
        "sandbox_mode": settings.sandbox_mode,
    }
