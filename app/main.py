import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import app_lifespan
from app.core.config import ALLOWED_ORIGINS, API_BASE_PATH, API_VERSION
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routers import all_routers

log = logging.getLogger("synthetic_soul.api")

app = FastAPI(
    title="Synthetic Soul API",
    version=API_VERSION,
    description="A digital replication of human-like thought processes and emotional fluctuation",
    lifespan=app_lifespan,
    openapi_tags=[
        {"name": "root", "description": "Misc root endpoints."},
        {"name": "messages", "description": "Submit and process messages."},
        {"name": "jobs", "description": "Job status polling."},
        {"name": "agents", "description": "Agents registry endpoints."},
        {"name": "meta", "description": "Service metadata (health, version)."},
        {"name": "auth", "description": "Authentication and session endpoints."},
        {"name": "thoughts", "description": "Agent thought retrieval endpoints."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,    # set to True only if you send cookies/Authorization
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Content-Type","Authorization", "X-CSRF-Token", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

app.mount("/static", StaticFiles(directory="app/assets"), name="static")


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def _error_body(code: str, message: str, request_id: str):
    return {"error": {"code": code, "message": message, "request_id": request_id}}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    detail = exc.detail
    code = detail if isinstance(detail, str) else "http_error"
    message = "Request failed."
    if exc.status_code == 401:
        message = "Authentication failed."
    elif exc.status_code == 403:
        message = "Not authorized."
    elif exc.status_code == 404:
        message = "Resource not found."
    elif exc.status_code == 422:
        message = "Request validation failed."
    elif exc.status_code == 429:
        message = "Rate limit exceeded."

    response = JSONResponse(
        status_code=exc.status_code,
        content=_error_body(code=code, message=message, request_id=request_id),
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    response = JSONResponse(
        status_code=422,
        content={
            **_error_body(code="validation_error", message="Request validation failed.", request_id=request_id),
            "details": exc.errors(),
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    log.exception("Unhandled error request_id=%s", request_id, exc_info=exc)
    response = JSONResponse(
        status_code=500,
        content=_error_body(code="internal_error", message="An unexpected error occurred.", request_id=request_id),
    )
    response.headers["X-Request-ID"] = request_id
    return response


# Routers
for r in all_routers:
    app.include_router(r, prefix=API_BASE_PATH)
