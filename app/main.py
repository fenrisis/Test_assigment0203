from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

from app.api.router import router
from app.api.websocket import websocket_endpoint

app = FastAPI(
    title="Chat API",
    description="Real-time chat application with WebSocket and REST API",
    version="1.0.0",
)


app.include_router(router)


app.websocket("/ws/{user_id}")(websocket_endpoint)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )
