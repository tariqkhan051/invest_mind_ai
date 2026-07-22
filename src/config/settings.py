"""Application settings using Pydantic Settings and YAML configuration files."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


def _load_yaml_config(environment: str) -> dict[str, Any]:
    """Load environment-specific YAML configuration."""
    config_path = CONFIG_DIR / f"{environment}.yaml"
    if not config_path.exists():
        return {}
    with config_path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _load_named_yaml(name: str) -> dict[str, Any]:
    """Load a named YAML configuration file from config/."""
    config_path = CONFIG_DIR / name
    if not config_path.exists():
        return {}
    with config_path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


class Settings(BaseSettings):
    """Central application settings.

    Environment variables take precedence over YAML configuration.
    See docs/08_PROJECT_STRUCTURE.md and docs/10_TECH_STACK.md.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="InvestMind AI", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    database_url: str = Field(
        default="sqlite:///./data/invest_mind_ai.db",
        alias="DATABASE_URL",
    )
    database_echo: bool = Field(default=False)

    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")
    shariah_mode: bool = Field(default=True, alias="SHARIAH_MODE")
    default_monthly_investment: int = Field(
        default=50_000,
        alias="DEFAULT_MONTHLY_INVESTMENT",
    )

    yaml_config: dict[str, Any] = Field(default_factory=dict, exclude=True)
    features_config: dict[str, Any] = Field(default_factory=dict, exclude=True)
    risk_config: dict[str, Any] = Field(default_factory=dict, exclude=True)
    providers_config: dict[str, Any] = Field(default_factory=dict, exclude=True)
    notifications_config: dict[str, Any] = Field(default_factory=dict, exclude=True)
    logging_config: dict[str, Any] = Field(default_factory=dict, exclude=True)

    @field_validator("environment")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        """Normalize environment name."""
        return value.lower().strip()

    def model_post_init(self, __context: Any) -> None:
        """Load YAML configuration after environment variables are applied."""
        self.yaml_config = _load_yaml_config(self.environment)
        self.features_config = _load_named_yaml("features.yaml")
        self.risk_config = _load_named_yaml("risk.yaml")
        self.providers_config = _load_named_yaml("providers.yaml")
        self.notifications_config = _load_named_yaml("notifications.yaml")
        self.logging_config = _load_named_yaml("logging.yaml")

        if (
            self.yaml_config.get("debug") is not None
            and "DEBUG" not in self.model_fields_set
        ):
            self.debug = bool(self.yaml_config["debug"])

        database_config = self.yaml_config.get("database", {})
        if database_config.get("echo") is not None:
            self.database_echo = bool(database_config["echo"])

        logging_config = self.yaml_config.get("logging", {})
        if logging_config.get("level") and "LOG_LEVEL" not in self.model_fields_set:
            self.log_level = str(logging_config["level"])

    @property
    def is_testing(self) -> bool:
        """Return True when running in the testing environment."""
        return self.environment == "testing"

    @property
    def is_production(self) -> bool:
        """Return True when running in the production environment."""
        return self.environment == "production"

    @property
    def cors_origins(self) -> list[str]:
        """Return configured CORS origins."""
        api_config = self.yaml_config.get("api", {})
        origins = api_config.get("cors_origins", [])
        return [str(origin) for origin in origins]

    @property
    def project_root(self) -> Path:
        """Return the project root directory."""
        return PROJECT_ROOT


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
