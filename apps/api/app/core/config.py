from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "GrantAtlas"
    environment: str = "local"
    database_url: str = "sqlite:///./grantatlas.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = Field(default="dev-only-change-me", min_length=16)
    access_token_expire_minutes: int = 720
    cookie_secure: bool = False
    cors_origins: str = "http://localhost:3000"
    web_base_url: str = "http://localhost:3000"
    grants_gov_search_url: str = "https://api.grants.gov/v1/api/search2"
    grants_gov_fetch_limit: int = 50
    sam_gov_api_key: str | None = None
    sam_gov_opportunities_url: str = "https://api.sam.gov/opportunities/v2/search"
    sam_gov_fetch_limit: int = 50
    sam_gov_default_posted_days: int = 30
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_starter_price_id: str | None = None
    stripe_professional_price_id: str | None = None
    stripe_growth_price_id: str | None = None
    stripe_enterprise_price_id: str | None = None
    stripe_trial_days: int = 14
    resend_api_key: str | None = None
    email_from: str = "GrantAtlas <notifications@example.com>"
    bootstrap_admin_email: str = "owner@gratitech.org"
    bootstrap_admin_password: str = "ChangeMe123!"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
