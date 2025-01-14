from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from app.constants.constants import (MIN_EMOTION_VALUE, MAX_EMOTION_VALUE)

class EmotionTraitSchema(BaseModel):
    description: str
    value: Optional[int] = Field(default=MIN_EMOTION_VALUE)
    min: Optional[int] = Field(default=MIN_EMOTION_VALUE)
    max: Optional[int] = Field(default=MAX_EMOTION_VALUE)

class EmotionSchema(BaseModel):
    happiness: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling joy, contentment, and pleasure. Scale: {MIN_EMOTION_VALUE} (no happiness) to {MAX_EMOTION_VALUE} (extremely joyful)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    anger: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling frustration, irritation, or rage. Scale: {MIN_EMOTION_VALUE} (no anger) to {MAX_EMOTION_VALUE} (extremely angry)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    sadness: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling sorrow, grief, or disappointment. Scale: {MIN_EMOTION_VALUE} (no sadness) to {MAX_EMOTION_VALUE} (deeply sorrowful)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    fear: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling anxiety, dread, or apprehension. Scale: {MIN_EMOTION_VALUE} (no fear) to {MAX_EMOTION_VALUE} (extremely fearful)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    surprise: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling caught off guard or astonished. Scale: {MIN_EMOTION_VALUE} (no surprise) to {MAX_EMOTION_VALUE} (completely astonished)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    disgust: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling revulsion or strong aversion. Scale: {MIN_EMOTION_VALUE} (no disgust) to {MAX_EMOTION_VALUE} (extremely disgusted)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    love: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling affection, attachment, or deep emotional bonds. Scale: {MIN_EMOTION_VALUE} (no love) to {MAX_EMOTION_VALUE} (deeply loving)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    guilt: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling remorse or responsibility for perceived wrongdoings. Scale: {MIN_EMOTION_VALUE} (no guilt) to {MAX_EMOTION_VALUE} (overwhelming guilt)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    shame: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling inadequacy, dishonor, or embarrassment. Scale: {MIN_EMOTION_VALUE} (no shame) to {MAX_EMOTION_VALUE} (extremely ashamed)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    pride: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling self-respect, accomplishment, or satisfaction in their achievements. Scale: {MIN_EMOTION_VALUE} (no pride) to {MAX_EMOTION_VALUE} (immense pride)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    hope: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling optimistic about the future. Scale: {MIN_EMOTION_VALUE} (no hope) to {MAX_EMOTION_VALUE} (extremely hopeful)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    gratitude: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling thankful and appreciative for positive aspects of their life. Scale: {MIN_EMOTION_VALUE} (no gratitude) to {MAX_EMOTION_VALUE} (deeply grateful)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    envy: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling jealousy or covetousness. Scale: {MIN_EMOTION_VALUE} (no envy) to {MAX_EMOTION_VALUE} (deeply envious)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    compassion: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling empathy and care for others. Scale: {MIN_EMOTION_VALUE} (no compassion) to {MAX_EMOTION_VALUE} (deeply compassionate)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    serenity: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling calm, peaceful, and untroubled. Scale: {MIN_EMOTION_VALUE} (no serenity) to {MAX_EMOTION_VALUE} (extremely serene)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    frustration: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling irritation or obstacles in achieving goals. Scale: {MIN_EMOTION_VALUE} (no frustration) to {MAX_EMOTION_VALUE} (deeply frustrated)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    contentment: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling satisfied and at peace with their situation. Scale: {MIN_EMOTION_VALUE} (no contentment) to {MAX_EMOTION_VALUE} (deeply content)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    anxiety: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling nervousness, worry, or unease. Scale: {MIN_EMOTION_VALUE} (no anxiety) to {MAX_EMOTION_VALUE} (extremely anxious)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    loneliness: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling isolated or disconnected. Scale: {MIN_EMOTION_VALUE} (no loneliness) to {MAX_EMOTION_VALUE} (deeply lonely)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    embarrassment: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling self-conscious or uncomfortable. Scale: {MIN_EMOTION_VALUE} (no embarrassment) to {MAX_EMOTION_VALUE} (deeply embarrassed)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    trust: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling safe and secure in relying on others. Scale: {MIN_EMOTION_VALUE} (no trust) to {MAX_EMOTION_VALUE} (deeply trusting)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    relief: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling ease after stress. Scale: {MIN_EMOTION_VALUE} (no relief) to {MAX_EMOTION_VALUE} (deeply relieved)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    affection: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling and expressing fondness toward others. Scale: {MIN_EMOTION_VALUE} (no affection) to {MAX_EMOTION_VALUE} (extremely affectionate)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    bitterness: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling resentment or disappointment. Scale: {MIN_EMOTION_VALUE} (no bitterness) to {MAX_EMOTION_VALUE} (deeply bitter)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    excitement: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling enthusiasm or eager anticipation. Scale: {MIN_EMOTION_VALUE} (no excitement) to {MAX_EMOTION_VALUE} (extremely excited)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    self_loathing: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling self-hate or a negative self-perception. Scale: {MIN_EMOTION_VALUE} (no self-loathing) to {MAX_EMOTION_VALUE} (deeply self-loathing)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )
    love_for_self: EmotionTraitSchema = Field(
        default=EmotionTraitSchema(
            description=f"The intensity with which they are feeling affection and appreciation for themselves. Scale: {MIN_EMOTION_VALUE} (no self-love) to {MAX_EMOTION_VALUE} (deeply self-loving)",
            value=MIN_EMOTION_VALUE,
            min=MIN_EMOTION_VALUE,
            max=MAX_EMOTION_VALUE,
        )
    )

class EmotionModifierSchema(BaseModel):
    modifier: EmotionSchema = Field(default_factory=EmotionSchema)
    reason: Optional[str] = "This person has no lasting impact over how they feel."

class EmotionStatusSchema(BaseModel):
    emotions: EmotionSchema = Field(default_factory=EmotionSchema)
    reason: Optional[str] = ""
