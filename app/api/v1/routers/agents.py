from datetime import datetime
from typing import Any
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from bson.json_util import dumps

from app.services.database import get_all_agents, grab_self
from app.core.config import BOT_NAME

router = APIRouter(prefix="/agents", tags=["agents"])

def to_aliased_mongo_shape(obj: Any) -> Any:
    """
    Recursively transform Mongo types so they match the JasmineModel aliases:
    - ObjectId -> {"$oid": "..."}
    - datetime -> {"$date": datetime}  (Pydantic will isoformat on output)
    """
    if isinstance(obj, ObjectId):
        return {"$oid": str(obj)}
    if isinstance(obj, datetime):
        return {"$date": obj}
    if isinstance(obj, dict):
        return {k: to_aliased_mongo_shape(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_aliased_mongo_shape(v) for v in obj]
    return obj

@router.get("/all")
async def get_agents():
    try:
        response = await get_all_agents()
        return {"agents": response}
    except Exception as e:
        print(f"Error in agents endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
async def get_active_agent():
    try:
        '''
        raw = await grab_self(BOT_NAME)  # whatever your data source returns
        shaped = to_aliased_mongo_shape(raw)
        model = JasmineModel.model_validate(shaped)  # Pydantic v2
        return model  # FastAPI will serialize using field aliases by default
        '''
        response = await grab_self(BOT_NAME)
        return {"agent": response}
    except Exception as e:
        print(f"Error in agent endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))