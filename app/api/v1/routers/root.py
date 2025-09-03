from fastapi import APIRouter, HTTPException
from app.core.config import AGENT_NAME

router = APIRouter(tags=["root"]) # no prefix; mounted at "/"

@router.get("/")
async def root():
    try:
        return {"active_agent": AGENT_NAME}
    except Exception as e:
        print(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))