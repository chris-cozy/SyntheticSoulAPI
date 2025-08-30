from fastapi import APIRouter, HTTPException, Response
from bson.json_util import dumps
from rq import Queue

from app.domain.models import MessageRequest
from app.core.redis_queue import get_queue


router = APIRouter(prefix="/v1/messages", tags=["messages"])


@router.post("/submit")
async def submit_message(request: MessageRequest):
    try:
        q: Queue = get_queue()
        job = q.enqueue(
            "app.tasks.send_message_task", # dotted path to worker function
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