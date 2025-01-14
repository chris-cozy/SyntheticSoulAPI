from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from app.constants.constants import NO_INTRINSIC_RELATIONSHIP
from app.models.emotions import EmotionStatusSchema
from app.models.personality import PersonalitySchema
from app.models.sentiments import SentimentMatrixSchema
from app.models.thoughts import ThoughtSchema

class ActivitySchema(BaseModel):
    name: Optional[str] = "Quiescence."
    category: Optional[str] = "custom"
    item: Optional[str] = "None"
    reason: Optional[str] = "Simply existing."
    start_time: datetime

class MemorySchema(BaseModel):
    memory_id: UUID = Field(default_factory=UUID)
    event: str
    thoughts: str
    timestamp: datetime

class SelfSchema(BaseModel):
    self_id: UUID = Field(default_factory=UUID)
    name: str
    identity: Optional[str] = "I am a prototype program made by cozycharm, designed as a digital replication of the human mind."
    personality_matrix: Optional[PersonalitySchema] = None
    memory_profile: List[MemorySchema] = []
    emotional_status: Optional[EmotionStatusSchema] = None
    latest_thought: Optional[ThoughtSchema] = None
    activity_status: Optional[ActivitySchema] = None

class UserSchema(BaseModel):
    user_id: UUID = Field(default_factory=UUID)
    name: str
    discord_id: str
    summary: Optional[str] = ""
    intrinsic_relationship: Optional[str] = NO_INTRINSIC_RELATIONSHIP
    extrinsic_relationship: Optional[str] = "stranger"
    memory_profile: List[MemorySchema] = []
    sentiment_status: Optional[SentimentMatrixSchema] = None
    last_interaction: Optional[datetime] = Field(default_factory=datetime.now)