from fastapi import APIRouter
from app.core.config import AGENT_NAME

router = APIRouter(tags=["root"]) # no prefix; mounted at "/"

@router.get("/")
async def root():
    return {"active_agent": AGENT_NAME}
