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

    # MVP flat rates; a data-driven fees_rules table (per country/provider/KYC
    # level) replaces these once the fee catalogue grows past the pilot.
    topup_fee_percent: str = "0.02"
    payment_fee_percent: str = "0.03"

    # Bootstrap super_admin created by the seed migration — change immediately
    # in any non-sandbox environment.
    admin_bootstrap_email: str = "admin@nasrcash.com"
    admin_bootstrap_password: str = "ChangeMe123!"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
