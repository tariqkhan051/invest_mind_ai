"""Database engine and session management."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import Settings
from src.core.exceptions import DatabaseError


def _create_engine(settings: Settings) -> Engine:
    """Create a SQLAlchemy engine from settings."""
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


@lru_cache
def get_engine(database_url: str, database_echo: bool) -> Engine:
    """Return a cached engine for the given database URL."""
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        database_url,
        echo=database_echo,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def get_session_factory(settings: Settings) -> sessionmaker[Session]:
    """Create a session factory bound to the configured engine."""
    engine = _create_engine(settings)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session(settings: Settings) -> Generator[Session]:
    """Yield a database session for FastAPI dependency injection."""
    session_factory = get_session_factory(settings)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_connection(settings: Settings) -> bool:
    """Verify database connectivity for readiness checks."""
    try:
        engine = _create_engine(settings)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        raise DatabaseError(f"Database connection failed: {exc}") from exc


def init_database(settings: Settings) -> None:
    """Create database tables for models that inherit from Base."""
    import src.database.models  # noqa: F401
    from src.database.base import Base

    engine = _create_engine(settings)
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_nav_columns(engine)


def _ensure_sqlite_nav_columns(engine: Engine) -> None:
    """Add newer nav_history columns on existing SQLite databases."""
    if engine.dialect.name != "sqlite":
        return
    alterations = (
        ("offer_price", "NUMERIC(19, 6)"),
        ("repurchase_price", "NUMERIC(19, 6)"),
        ("fytd_return", "NUMERIC(10, 6)"),
        ("mtd_return", "NUMERIC(10, 6)"),
        ("category", "VARCHAR(120)"),
    )
    with engine.begin() as connection:
        existing = {
            row[1] for row in connection.execute(text("PRAGMA table_info(nav_history)"))
        }
        if not existing:
            return
        for column_name, column_type in alterations:
            if column_name in existing:
                continue
            connection.execute(
                text(f"ALTER TABLE nav_history ADD COLUMN {column_name} {column_type}")
            )
