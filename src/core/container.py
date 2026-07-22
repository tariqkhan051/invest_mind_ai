"""Lightweight dependency injection container.

See docs/03_ARCHITECTURE.md and docs/08_PROJECT_STRUCTURE.md §core.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from src.config.settings import Settings, get_settings
from src.database.session import get_session_factory

T = TypeVar("T")


@dataclass
class Container:
    """Application service container for dependency resolution."""

    settings: Settings = field(default_factory=get_settings)
    _session_factory: Callable[[], Session] | None = field(default=None, init=False)
    _singletons: dict[str, Any] = field(default_factory=dict, init=False)

    def session_factory(self) -> Callable[[], Session]:
        """Return the SQLAlchemy session factory."""
        if self._session_factory is None:
            self._session_factory = get_session_factory(self.settings)
        return self._session_factory

    def db_session(self) -> Session:
        """Create a new database session."""
        return self.session_factory()()

    def register_singleton(self, key: str, instance: Any) -> None:
        """Register a singleton instance for testing or extension."""
        self._singletons[key] = instance

    def get_singleton(self, key: str) -> Any:
        """Retrieve a registered singleton."""
        return self._singletons[key]


_container: Container | None = None


def get_container() -> Container:
    """Return the global application container."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def reset_container() -> None:
    """Reset the global container — used in tests."""
    global _container
    _container = None
