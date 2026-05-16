from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from core.models import ErrorResponse
from services.exceptions import UpstreamRateLimitError, UpstreamServiceError


def _error_response(status_code: int, error: str, detail: str, code: str) -> JSONResponse:
    payload = ErrorResponse(error=error, detail=detail, code=code)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error="Validation Error",
        detail=str(exc),
        code="VALIDATION_ERROR",
    )


async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="Internal Server Error",
        detail=str(exc),
        code="INTERNAL_ERROR",
    )


async def upstream_rate_limit_handler(_: Request, exc: UpstreamRateLimitError) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        error="Upstream Rate Limit",
        detail=str(exc),
        code="UPSTREAM_RATE_LIMIT",
    )


async def upstream_service_error_handler(_: Request, exc: UpstreamServiceError) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_502_BAD_GATEWAY,
        error="Upstream Service Error",
        detail=str(exc),
        code="UPSTREAM_SERVICE_ERROR",
    )
