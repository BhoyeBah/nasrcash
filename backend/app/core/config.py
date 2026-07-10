from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://nasrcash:nasrcash@localhost:5432/nasrcash"
    database_url_sync: str = "postgresql+psycopg2://nasrcash:nasrcash@localhost:5432/nasrcash"

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me-in-production-please"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    sandbox_mode: bool = True
    kyc_storage_path: str = "./storage/kyc"

    default_country_code: str = "GN"
    default_currency_code: str = "GNF"

    otp_expire_seconds: int = 300
    max_login_attempts: int = 5
    login_lockout_minutes: int = 15

    # Bootstrap super_admin created by the seed migration — change immediately
    # in any non-sandbox environment.
    admin_bootstrap_email: str = "admin@nasrcash.com"
    admin_bootstrap_password: str = "ChangeMe123!"

    # Compliance/risk detection thresholds (not per-country/KYC scoped like
    # fees and limits — these are fraud-monitoring heuristics, not pricing).
    compliance_large_transaction_threshold: int = 3_000_000
    compliance_velocity_window_minutes: int = 10
    compliance_velocity_max_count: int = 5

    # Aggregate risk score (weighted sum of open/reviewing alerts over a
    # rolling window) at or above which an account is auto-frozen.
    compliance_risk_auto_freeze_threshold: int = 15
    compliance_risk_window_days: int = 30

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
