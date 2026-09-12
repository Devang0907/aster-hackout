from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Industrial Emission Leak-Point Detector API"
    app_env: Literal["development", "test", "production"] = "development"
    debug: bool = False
    database_url: SecretStr | None = None
    auth_mode: Literal["jwt", "development_header"] = "jwt"
    jwt_secret: SecretStr | None = None
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    jwt_audience: str | None = None
    jwt_issuer: str | None = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from_email: str | None = None
    email_otp_expiry_seconds: int = 600
    carbonwise_demo_password: SecretStr | None = None
    openrouter_api_key: SecretStr | None = None
    openrouter_model: str = "openrouter/free"
    openrouter_http_referer: str = "http://localhost:8080"
    openrouter_app_title: str = "CarbonLoop"
    cors_origins: str = ""
    cors_origin_regex: str | None = None

    model_config = SettingsConfigDict(
        env_file=(BACKEND_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_security_mode(self) -> "Settings":
        if self.app_env == "production" and self.auth_mode == "development_header":
            raise ValueError("development_header authentication is forbidden in production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        """Return the configured CORS origins as a list."""
        if not self.cors_origins:
            return []
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def cors_origin_regex_value(self) -> str | None:
        """Allow Vite/localhost dev ports without locking to a single port."""
        if self.cors_origin_regex:
            return self.cors_origin_regex
        if self.app_env == "development":
            return r"https?://(localhost|127\.0\.0\.1)(:\d+)?$"
        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()
