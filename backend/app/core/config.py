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
    cors_origins: list[str] = []

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
