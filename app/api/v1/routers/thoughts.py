from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.services.database import get_thoughts

router = APIRouter(prefix="/thoughts", tags=["thoughts"])
    
@router.get("/latest")
async def get_latest_thought():
    try:
        doc = await get_thoughts(1)
        if not doc:
            raise HTTPException(status_code=404, detail="Thought not found")
        
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
        return {"latest_thought": payload}
    except Exception as e:
        print(f"Error in thought endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))