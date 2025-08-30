from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import lifespan
from app.core.config import ALLOWED_ORIGINS, API_VERSION

from app.api.v1.routers.root import router as root_router
from app.api.v1.routers.messages import router as messages_router
from app.api.v1.routers.jobs import router as jobs_router
from app.api.v1.routers.agents import router as agents_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,    # set to True only if you send cookies/Authorization
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Content-Type","Authorization"],
    expose_headers=[],
)

# Routers
app.include_router(root_router, prefix="/v1")
app.include_router(messages_router, prefix="/v1")
app.include_router(jobs_router, prefix="/v1")
app.include_router(agents_router, prefix="/v1")

@app.get("/version", tags=["meta"])
async def version():
    return {"version": API_VERSION}