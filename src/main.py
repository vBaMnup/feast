from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from src.config import settings
from src.reservation.router import router as reservation_router
from src.tables.router import router as table_router

app = FastAPI(title="Feast API")

app.include_router(table_router)
app.include_router(reservation_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Попробуйте позже."},
    )


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
