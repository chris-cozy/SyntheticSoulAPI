from fastapi import APIRouter
from app.core.config import API_VERSION

router = APIRouter(prefix="/meta", tags=["meta"])

@router.get("/version")
async def version():
    return {"version": API_VERSION}


@router.get("/ping")
async def ping():
    return {"status": "ok"}