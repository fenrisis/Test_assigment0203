from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from app.api.router import router
from app.api.websocket import websocket_endpoint

app = FastAPI(
    title="Chat API",
    description="Real-time chat application with WebSocket and REST API",
    version="1.0.0",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["paths"]["/ws/{user_id}"] = {
        "get": {
            "tags": ["websocket"],
            "summary": "WebSocket Chat Connection",
            "description": "Connect to chat as user",
            "parameters": [
                {
                    "name": "user_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "User ID"
                }
            ],
            "responses": {
                "101": {
                    "description": "WebSocket upgrade successful"
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(router)
app.websocket("/ws/{user_id}")(websocket_endpoint)