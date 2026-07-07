from fastapi import Request, status
from fastapi.responses import JSONResponse


class NasrCashError(Exception):
    """Base class for all business/domain errors in NasrCash."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    error_code: str = "nasrcash_error"

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(message)


class NotFoundError(NasrCashError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ValidationError(NasrCashError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "validation_error"


class UnauthorizedError(NasrCashError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"


class ForbiddenError(NasrCashError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"


class ConflictError(NasrCashError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


class InsufficientBalanceError(NasrCashError):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    error_code = "insufficient_balance"


class RateLimitError(NasrCashError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limited"


class LedgerImbalanceError(NasrCashError):
    """Raised when a ledger transaction's debits and credits do not balance.

    This must never happen in normal operation — it indicates a bug in the
    caller, not a user-facing condition.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "ledger_imbalance"


async def nasrcash_exception_handler(request: Request, exc: NasrCashError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message},
    )


def register_exception_handlers(app) -> None:
    app.add_exception_handler(NasrCashError, nasrcash_exception_handler)
