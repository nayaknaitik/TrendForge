"""
Application-wide exception classes and error handlers.

Provides a consistent error response format across all endpoints.
"""

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from starlette.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Base Exceptions ─────────────────────────────────────────────────────

class TrendForgeError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str = "internal_error", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(TrendForgeError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="not_found",
            status_code=404,
        )


class AuthenticationError(TrendForgeError):
    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(message=message, code="authentication_error", status_code=401)


class AuthorizationError(TrendForgeError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="authorization_error", status_code=403)


class ValidationError(TrendForgeError):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message=message, code="validation_error", status_code=422)
        self.field = field


class RateLimitError(TrendForgeError):
    def __init__(self):
        super().__init__(
            message="Rate limit exceeded",
            code="rate_limit_exceeded",
            status_code=429,
        )


class ExternalServiceError(TrendForgeError):
    """Raised when an external API (Twitter, Reddit, OpenAI, etc.) fails."""

    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"External service error [{service}]: {message}",
            code="external_service_error",
            status_code=502,
        )
        self.service = service


class AIAgentError(TrendForgeError):
    """Raised when an AI agent fails to produce valid output."""

    def __init__(self, agent_name: str, message: str):
        super().__init__(
            message=f"AI agent error [{agent_name}]: {message}",
            code="ai_agent_error",
            status_code=500,
        )
        self.agent_name = agent_name


# ── Error Handlers ──────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(TrendForgeError)
    async def trendforge_error_handler(request: Request, exc: TrendForgeError) -> JSONResponse:
        logger.error(
            "application_error",
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url),
        )
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.code,
                "message": exc.message,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_error",
            error_type=type(exc).__name__,
            message=str(exc),
            path=str(request.url),
        )
        return ORJSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred" if True else str(exc),
                "path": str(request.url.path),
            },
        )
