from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response
from bson.json_util import dumps
from fastapi.encoders import jsonable_encoder
from rq import Queue

from app.domain.models import MessageRequest
from app.core.redis_queue import get_queue
from app.services.auth import auth_guard, identity
from app.services.database import ensure_user_and_profile, get_conversation
from app.tasks import send_message_task


router = APIRouter(prefix="/messages", tags=["messages"], dependencies=[Depends(auth_guard)])


@router.post("/submit")
async def submit_message(request: MessageRequest, ident = Depends(identity)):
    user_id, token_username, _sid = ident
    request.user_id = user_id
    request.username = token_username
        
    # Ensure the identity + perspective exists (idempotent)
    if request.user_id and request.username:
        await ensure_user_and_profile(request.user_id, request.username)
        
    try:
        q: Queue = get_queue()
        job = q.enqueue(
            send_message_task,
            request.model_dump(), # pydantic -> dict
            job_timeout=600,
        )

        # return 202 + Location header so clients can poll
        response = Response(
            content=dumps({"job_id": job.id, "status": job.get_status()}),
            status_code=202,
            headers={
                "Location": f"/jobs/{job.id}",
                "Retry-After": "3",
            },
            media_type="application/json",
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/conversation")
async def get_user_conversation(ident = Depends(identity)):
    user_id, token_username, _sid = ident
    username = token_username
        
    # Ensure the identity + perspective exists (idempotent)
    if username:
        await ensure_user_and_profile(user_id, username)
        
    try:
        doc = await get_conversation(username)
        if not doc:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
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
        return {"conversation": payload}
    except Exception as e:
        print(f"Error in conversation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))