import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from api.errors import (
    generic_exception_handler,
    upstream_rate_limit_handler,
    upstream_service_error_handler,
    validation_exception_handler,
)
from api.middleware import request_logging_middleware
from api.routers.health import router as health_router
from api.routers.ingest import router as ingest_router
from api.routers.query import router as query_router
from api.routers.sources import router as sources_router
from api.routers.ui import router as ui_router
from core.config import settings
from services.exceptions import UpstreamRateLimitError, UpstreamServiceError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.middleware("http")(request_logging_middleware)

app.include_router(ui_router)
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(sources_router)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(UpstreamRateLimitError, upstream_rate_limit_handler)
app.add_exception_handler(UpstreamServiceError, upstream_service_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)
