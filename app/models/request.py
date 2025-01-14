from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class MessageRequest(BaseModel):
    message: str
    user_id: str
    user_name: str

class MessageResponse(BaseModel):
    response: str