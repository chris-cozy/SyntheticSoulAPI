from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field

MessageType = Literal["dm", "group"]

class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    type: MessageType
    
class InternalMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    user_id: str
    type: MessageType

class MessageResponse(BaseModel):
    response: Optional[str]
    time: int
    expression: str


class JobSubmissionResponse(BaseModel):
    job_id: str
    status: str
    
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    
class GenerateReplyTaskResponse(BaseModel):
    message_response: MessageResponse
    user_id: str
    queries: List[Any]
