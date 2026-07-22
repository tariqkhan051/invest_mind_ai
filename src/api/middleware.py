"""HTTP middleware for request logging and error handling."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.api.schemas import ApiErrorResponse, ErrorDetail
from src.config.settings import Settings
from src.core.exceptions import InvestMindError
from src.core.logging import get_logger

logger = get_logger("api.middleware")


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """Register all HTTP middleware on the FastAPI application."""
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.middleware("http")
    async def request_logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Log incoming requests and response timing."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        logger.info(
            "request_started method={} path={} request_id={}",
            request.method,
            request.url.path,
            request_id,
        )

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed method={} path={} status={} duration_ms={:.2f} "
            "request_id={}",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        return response


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(InvestMindError)
    async def investmind_error_handler(
        _request: Request,
        exc: InvestMindError,
    ) -> JSONResponse:
        """Handle domain and application errors."""
        logger.warning("application_error message={}", exc.message)
        payload = ApiErrorResponse(
            message=exc.message,
            errors=[ErrorDetail(message=exc.message)],
        )
        return JSONResponse(status_code=400, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected errors without exposing internals."""
        logger.exception("unhandled_error error={}", str(exc))
        payload = ApiErrorResponse(
            message="An unexpected error occurred.",
            errors=[ErrorDetail(message="Internal server error")],
        )
        return JSONResponse(status_code=500, content=payload.model_dump())
