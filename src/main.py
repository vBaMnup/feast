import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Импортируем settings
from src.config import settings
from src.logging_config import setup_logging
from src.reservation.router import router as reservation_router
from src.tables.router import router as table_router

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown sequence.

    Args:
        app (FastAPI): The FastAPI application.

    Yields:
        None
    """

    logger.info("Application startup sequence initiated.")
    yield
    logger.info("Application shutdown sequence initiated.")


# Используем настройки из settings
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",  # Путь для Swagger UI
    redoc_url=f"{settings.API_PREFIX}/redoc",  # Путь для ReDoc
)

# Используем settings.API_PREFIX
app.include_router(table_router, prefix=settings.API_PREFIX)
app.include_router(reservation_router, prefix=settings.API_PREFIX)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for HTTPExceptions.

    Args:
        request (Request): The request object.
        exc (HTTPException): The exception object.

    Returns:
        JSONResponse: The response object.
    """

    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for uncaught exceptions.

    Args:
        request (Request): The request object.
        exc (Exception): The exception object.

    Returns:
        JSONResponse: The response object.
    """

    logger.exception(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Попробуйте позже."},
    )


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint."""

    logger.debug("Health check requested.")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=True,
    )
