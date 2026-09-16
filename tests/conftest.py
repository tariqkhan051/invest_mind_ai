"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

TEST_DATABASE_URL = "sqlite:///./data/test_invest_mind_ai.db"

# Force a dedicated test database before importing application modules.
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["SCHEDULER_ENABLED"] = "false"

from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from src.api.app import create_app  # noqa: E402
from src.api.dependencies import get_app_settings, get_db  # noqa: E402
from src.config.settings import Settings, get_settings  # noqa: E402
from src.core.container import reset_container  # noqa: E402
from src.database.base import Base  # noqa: E402
from src.database.session import _create_engine  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_singletons(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Reset cached singletons between tests and pin the test database URL."""
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("SCHEDULER_ENABLED", "false")
    get_settings.cache_clear()
    reset_container()
    yield
    get_settings.cache_clear()
    reset_container()


@pytest.fixture
def test_settings() -> Settings:
    """Return settings configured for testing."""
    get_settings.cache_clear()
    return Settings(
        environment="testing",
        database_url=TEST_DATABASE_URL,
        debug=False,
        log_level="WARNING",
        scheduler_enabled=False,
    )


@pytest.fixture
def db_session(test_settings: Settings) -> Generator[Session]:
    """Provide a database session with a fresh schema."""
    import src.database.models  # noqa: F401

    engine = _create_engine(test_settings)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(
    test_settings: Settings,
    db_session: Session,
) -> Generator[TestClient]:
    """Return a FastAPI test client bound to the same DB session as fixtures."""
    get_settings.cache_clear()
    app = create_app(test_settings)

    def override_settings() -> Settings:
        return test_settings

    def override_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_app_settings] = override_settings
    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
