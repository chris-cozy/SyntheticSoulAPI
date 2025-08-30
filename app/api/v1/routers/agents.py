from fastapi import APIRouter, HTTPException
from bson.json_util import dumps

from app.services.database import get_all_agents, grab_self
from app.core.config import BOT_NAME

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/all")
async def get_agents():
    try:
        response = await get_all_agents()
        return {"agents": dumps(response)}
    except Exception as e:
        print(f"Error in agents endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
async def get_active_agent():
    try:
        response = await grab_self(BOT_NAME)
        return {"agent": dumps(response)}
    except Exception as e:
        print(f"Error in agent endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))