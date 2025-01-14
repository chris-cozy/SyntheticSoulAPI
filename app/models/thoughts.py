from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class ThoughtSchema(BaseModel):
    thought_id: UUID = Field(default_factory=UUID)
    thought: Optional[str] = ""
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)