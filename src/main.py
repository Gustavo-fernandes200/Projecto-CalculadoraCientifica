import flet as ft
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from Calculadora import main


class RemoveRestrictiveHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.__delitem__("cross-origin-embedder-policy") if "cross-origin-embedder-policy" in response.headers else None
        response.headers.__delitem__("cross-origin-opener-policy") if "cross-origin-opener-policy" in response.headers else None
        return response


app = ft.run(
    main,
    host="0.0.0.0",
    port=5000,
    view=ft.AppView.WEB_BROWSER,
    export_asgi_app=True,
)

app.add_middleware(RemoveRestrictiveHeaders)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, ws="websockets-sansio")
