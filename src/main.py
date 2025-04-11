from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from src.reservation.router import router as reservation_router
from src.tables.router import router as table_router

app = FastAPI(title="Feast API")

app.include_router(table_router)
app.include_router(reservation_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom exception handler for HTTP exceptions.

    Args:
        request (Request): The request object.
        exc (HTTPException): The HTTP exception.

    Returns:
        JSONResponse: A JSON response containing the error message.
    """

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for any uncaught exceptions.

    Args:
        request (Request): The request object.
        exc (Exception): The exception.

    Returns:
        JSONResponse: A JSON response containing a generic error message.
    """

    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Попробуйте позже."},
    )


@app.get("/health", tags=["Health"])
def health():
    """
    Health check endpoint.

    Returns:
        dict: A dictionary containing a status message.
    """

    return {"status": "ok"}
