"""Unit tests for application configuration."""

from src.config.settings import Settings


def test_settings_load_testing_defaults(test_settings: Settings) -> None:
    """Settings fixture should use the testing environment."""
    assert test_settings.environment == "testing"
    assert test_settings.is_testing is True
    assert test_settings.scheduler_enabled is False


def test_settings_load_yaml_features(test_settings: Settings) -> None:
    """Settings should load feature flags from YAML."""
    features = test_settings.features_config.get("features", {})
    assert features.get("mutual_fund_engine") is True
    assert features.get("ai_recommendations") is True


def test_settings_load_risk_config(test_settings: Settings) -> None:
    """Settings should load risk thresholds from YAML."""
    portfolio_risk = test_settings.risk_config.get("portfolio", {})
    assert portfolio_risk.get("max_single_fund_allocation") == 0.40
