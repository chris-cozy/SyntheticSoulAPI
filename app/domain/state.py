from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional

class BoundedTrait(BaseModel):
    value: int = Field(0, ge=0, le=100)
    min: int = 0
    max: int = 100
    description: Optional[str] = None

    def apply(self, delta: int) -> "BoundedTrait":
        v = max(self.min, min(self.max, self.value + delta))
        return self.model_copy(update={"value": v})

class EmotionalState(BaseModel):
    emotions: Dict[str, BoundedTrait]
    reason: Optional[str] = None

class PersonalityMatrix(BaseModel):
    # Use your lite keys or full keys based on mode
    traits: Dict[str, BoundedTrait]

class EmotionalDelta(BaseModel):
    deltas: Dict[str, int]  # e.g. {"joy": +6, "sadness": -3}
    reason: Optional[str] = None
    confidence: Optional[float] = Field(default=0.7, ge=0, le=1)

class PersonalityDelta(BaseModel):
    deltas: Dict[str, int]  # e.g. {"warmth": +2}
    reason: Optional[str] = None
    confidence: Optional[float] = Field(default=0.6, ge=0, le=1)