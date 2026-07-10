from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.kyc.router import router as kyc_router
from app.modules.notifications.router import router as notifications_router
from app.modules.cards.router import router as cards_router
from app.modules.sandbox.router import router as sandbox_router
from app.modules.support.router import router as support_router
from app.modules.topups.router import router as topups_router
from app.modules.wallets.router import router as wallets_router
from app.modules.withdrawals.router import router as withdrawals_router

settings = get_settings()

app = FastAPI(
    title="NasrCash API",
    description="Wallet local et cartes virtuelles internationales — MVP sandbox (Guinée / GNF)",
    version="0.1.0",
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(kyc_router)
app.include_router(wallets_router)
app.include_router(topups_router)
app.include_router(withdrawals_router)
app.include_router(cards_router)
app.include_router(notifications_router)
app.include_router(admin_router)
app.include_router(sandbox_router)
app.include_router(support_router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {
        "status": "ok",
        "environment": settings.environment,
        "sandbox_mode": settings.sandbox_mode,
    }
