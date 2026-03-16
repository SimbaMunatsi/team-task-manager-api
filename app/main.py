import logging

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.middleware.logging import RequestLoggingMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()