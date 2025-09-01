from pydantic import BaseModel, Field, conlist
from typing import List, Optional, Literal
from datetime import datetime

Significance = Literal["low","medium","high"]

class LightEmotion(BaseModel):
    # keep small to avoid doc bloat; values validated elsewhere
    value: int = Field(ge=0, le=100)

class EmotionalImpact(BaseModel):
    joy: Optional[LightEmotion] = None
    sadness: Optional[LightEmotion] = None
    anger: Optional[LightEmotion] = None
    fear: Optional[LightEmotion] = None
    surprise: Optional[LightEmotion] = None
    love: Optional[LightEmotion] = None
    disgust: Optional[LightEmotion] = None

class Memory(BaseModel):
    agent_name: str
    user: Optional[str] = None
    event: str
    thoughts: str
    significance: Significance = "low"
    emotional_impact: Optional[EmotionalImpact] = None
    tags: List[str] = Field(default_factory=list)
    ts_created: datetime = Field(default_factory=datetime.now)
    ts_last_accessed: Optional[datetime] = None
    recall_count: int = 0
    embedding: Optional[List[float]] = None  # vector for semantic search
    ttl_at: Optional[datetime] = None