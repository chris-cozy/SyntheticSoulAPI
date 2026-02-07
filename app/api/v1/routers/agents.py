from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from app.services.auth import auth_guard
from app.services.database import get_all_agents, grab_self

router = APIRouter(prefix="/agents", tags=["agents"], dependencies=[Depends(auth_guard)])

@router.get("/all")
async def get_agents():
    response = await get_all_agents()
    return {"agents": response}

@router.get("/active")
async def get_active_agent():
    doc = await grab_self()
    if not doc:
        raise HTTPException(status_code=404, detail="agent_not_found")

    # make a copy, expose id as string, drop Mongo's _id key (optional but common)
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))

    payload = jsonable_encoder(
        doc,
        custom_encoder={
            ObjectId: str,
            datetime: lambda d: d.isoformat()
        },
    )
    return {"agent": payload}
