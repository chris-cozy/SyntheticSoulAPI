from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from bson import ObjectId

class MessageSchema(BaseModel):
    message_id: Optional[UUID] = Field(default_factory=UUID)
    message: str
    purpose: str
    tone: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    sender: str
    is_bot: bool

class ConversationSchema(BaseModel):
    conversation_id: Optional[UUID] = Field(default_factory=UUID)
    user_id: str
    messages: List[MessageSchema] = []