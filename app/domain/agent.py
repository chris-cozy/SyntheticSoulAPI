from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ObjectId(BaseModel):
    oid: str = Field(..., alias="$oid")


class DateObject(BaseModel):
    date: datetime = Field(..., alias="$date")


class RangeValue(BaseModel):
    description: str
    value: int
    min: int
    max: int


class PersonalityMatrix(BaseModel):
    warmth: RangeValue
    playfulness: RangeValue
    trust_reliability: RangeValue
    curiosity_creativity: RangeValue
    empathy_compassion: RangeValue
    emotional_stability: RangeValue
    assertiveness_confidence: RangeValue
    adaptability: RangeValue
    discipline_responsibility: RangeValue
    perspective: RangeValue


class Personality(BaseModel):
    myers_briggs: str = Field(..., alias="myers-briggs")
    personality_matrix: PersonalityMatrix
    description: str


class MemoryProfile(BaseModel):
    all_tags: List[str]
    memories: List[str]  # You could replace with a structured model if needed.


class Emotions(BaseModel):
    joy: RangeValue
    sadness: RangeValue
    anger: RangeValue
    fear: RangeValue
    surprise: RangeValue
    love: RangeValue
    disgust: RangeValue


class EmotionalStatus(BaseModel):
    emotions: Emotions
    reason: str
    type: str
    joy: Optional[int] = None
    sadness: Optional[int] = None
    anger: Optional[Dict[str, int]] = None


class Thought(BaseModel):
    thought: str
    timestamp: DateObject


class AgentModel(BaseModel):
    id: ObjectId = Field(..., alias="_id")
    name: str
    identity: str
    personality: Personality
    memory_profile: MemoryProfile
    emotional_status: EmotionalStatus
    thoughts: List[Thought]
    birthdate: DateObject