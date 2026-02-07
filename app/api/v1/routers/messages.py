from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from rq import Queue

from app.domain.models import InternalMessageRequest, JobSubmissionResponse, MessageRequest
from app.core.config import API_BASE_PATH
from app.core.redis_queue import get_queue
from app.services.auth import _ratelimit, auth_guard, identity
from app.services.database import ensure_user_and_profile, get_conversation
from app.tasks import generate_reply_task


router = APIRouter(prefix="/messages", tags=["messages"], dependencies=[Depends(auth_guard)])


@router.post("/submit", response_model=JobSubmissionResponse, status_code=202)
async def submit_message(request: MessageRequest, ident = Depends(identity)):
    user_id, token_username, _sid = ident
    await _ratelimit(f"rl:submit:{user_id}", limit=60, window_sec=60)
    # Ensure the identity + perspective exists (idempotent)
    if user_id and token_username:
        await ensure_user_and_profile(user_id, token_username)

    q: Queue = get_queue()
    job = q.enqueue(
        generate_reply_task,
        InternalMessageRequest(message=request.message, type=request.type, user_id=user_id),
        job_timeout=600,
    )
    job.meta["owner_user_id"] = user_id
    job.save_meta()

    # return 202 + Location header so clients can poll
    response = JSONResponse(
        content={"job_id": job.id, "status": job.get_status()},
        status_code=202,
        headers={
            "Location": f"{API_BASE_PATH}/jobs/{job.id}",
            "Retry-After": "3",
        },
    )
    return response
    
@router.get("/conversation")
async def get_user_conversation(ident = Depends(identity)):
    user_id, token_username, _sid = ident
    username = token_username
        
    # Ensure the identity + perspective exists (idempotent)
    if username:
        await ensure_user_and_profile(user_id, username)
        
    doc = await get_conversation(user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="conversation_not_found")
    
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
