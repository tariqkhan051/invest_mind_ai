"""Application entry point."""

from __future__ import annotations

import uvicorn

from src.api.app import create_app
from src.config.settings import get_settings

app = create_app()


def run() -> None:
    """Run the application with Uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug and not settings.is_production,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
