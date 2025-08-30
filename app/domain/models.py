from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

class MessageRequest(BaseModel):
    message: str
    username: str
    type: str

class MessageResponse(BaseModel):
    response: Optional[str]
    time: int
    expression: str

class ExtendedMessageRequest(BaseModel):
    message: str
    sender: str
    timestamp: datetime
    
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None