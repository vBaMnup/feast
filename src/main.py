import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

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


app = FastAPI(title="Feast API", lifespan=lifespan)

app.include_router(table_router)
app.include_router(reservation_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
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
async def global_exception_handler(request: Request, exc: Exception):
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
async def health():
    """Health check endpoint."""

    logger.debug("Health check requested.")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
