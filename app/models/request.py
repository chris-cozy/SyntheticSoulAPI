from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class MessageRequest(BaseModel):
    message: str
    username: str
    type: str

class MessageResponse(BaseModel):
    response: Optional[str]
    time: int
    emote: str

class ExtendedMessageRequest(BaseModel):
    message: str
    sender: str
    timestamp: datetime
