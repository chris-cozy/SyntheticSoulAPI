from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import app_lifespan
from app.core.config import ALLOWED_ORIGINS, API_VERSION

from app.api.v1.routers import all_routers

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
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,    # set to True only if you send cookies/Authorization
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Content-Type","Authorization"],
    expose_headers=[],
)

# Routers
for r in all_routers:
    app.include_router(r, prefix="/v1")