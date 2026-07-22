"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

# Set test environment before importing application modules.
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/test_invest_mind_ai.db")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("SCHEDULER_ENABLED", "false")

from sqlalchemy.orm import Session, sessionmaker

from src.api.app import create_app
from src.config.settings import Settings, get_settings
from src.core.container import reset_container
from src.database.base import Base
from src.database.session import _create_engine


@pytest.fixture(autouse=True)
def _reset_singletons() -> Generator[None]:
    """Reset cached singletons between tests."""
    get_settings.cache_clear()
    reset_container()
    yield
    get_settings.cache_clear()
    reset_container()


@pytest.fixture
def test_settings() -> Settings:
    """Return settings configured for testing."""
    return Settings(
        environment="testing",
        database_url="sqlite:///./data/test_invest_mind_ai.db",
        debug=False,
        log_level="WARNING",
        scheduler_enabled=False,
    )


@pytest.fixture
def client(test_settings: Settings) -> Generator[TestClient]:
    """Return a FastAPI test client."""
    app = create_app(test_settings)
    with TestClient(app) as test_client:
        yield test_client


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
