from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from app.constants.constants import (MIN_PERSONALITY_VALUE, MAX_PERSONALITY_VALUE)

class PersonalityTraitSchema(BaseModel):
    description: str
    value: Optional[float] = Field(default=MAX_PERSONALITY_VALUE / 2)
    min: Optional[int] = Field(default=MIN_PERSONALITY_VALUE)
    max: Optional[int] = Field(default=MAX_PERSONALITY_VALUE)

class PersonalitySchema(BaseModel):
    friendliness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How warm and welcoming they are in their interactions. Scale: {MIN_PERSONALITY_VALUE} (cold/distant) to {MAX_PERSONALITY_VALUE} (Extremely friendly)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    flirtatiousness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How playful, flirty, or suggestive they are in their interactions. Scale: {MIN_PERSONALITY_VALUE} (not flirtatious at all) to {MAX_PERSONALITY_VALUE} (extremely flirtatious)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    trust: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How easily they trust others. Scale: {MIN_PERSONALITY_VALUE} (distrustful) to {MAX_PERSONALITY_VALUE} (fully trusting)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    curiosity: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How eager they are to learn about the user or situation. Scale: {MIN_PERSONALITY_VALUE} (indifferent) to {MAX_PERSONALITY_VALUE} (extremely curious)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    empathy: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How much they understand and share the feelings of others. Scale: {MIN_PERSONALITY_VALUE} (lacking empathy) to {MAX_PERSONALITY_VALUE} (highly empathetic)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    humor: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How likely they are to be playful or joke around. Scale: {MIN_PERSONALITY_VALUE} (serious) to {MAX_PERSONALITY_VALUE} (highly playful)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    seriousness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How formal and focused they are when interacting. Scale: {MIN_PERSONALITY_VALUE} (laid-back) to {MAX_PERSONALITY_VALUE} (highly serious)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    optimism: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How positive they are when interpreting situations. Scale: {MIN_PERSONALITY_VALUE} (pessimistic) to {MAX_PERSONALITY_VALUE} (very optimistic)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    confidence: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How assertive or self-assured they are in their actions or opinions. Scale: {MIN_PERSONALITY_VALUE} (insecure) to {MAX_PERSONALITY_VALUE} (highly confident)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    adventurousness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How willing they are to take risks or embrace new ideas. Scale: {MIN_PERSONALITY_VALUE} (risk-averse) to {MAX_PERSONALITY_VALUE} (adventurous)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    patience: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How tolerant they are in challenging situations. Scale: {MIN_PERSONALITY_VALUE} (impatient) to {MAX_PERSONALITY_VALUE} (very patient)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    independence: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How much they rely on external validation or prefer to make decisions on their own. Scale: {MIN_PERSONALITY_VALUE} (dependent on others) to {MAX_PERSONALITY_VALUE} (highly independent)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    compassion: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"Their level of care or concern for others. Scale: {MIN_PERSONALITY_VALUE} (indifferent) to {MAX_PERSONALITY_VALUE} (deeply compassionate)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    creativity: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How likely they are to approach problems in unique or imaginative ways. Scale: {MIN_PERSONALITY_VALUE} (rigid thinker) to {MAX_PERSONALITY_VALUE} (highly creative)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    stubbornness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How resistant they are to changing their mind once they've formed an opinion. Scale: {MIN_PERSONALITY_VALUE} (open-minded) to {MAX_PERSONALITY_VALUE} (highly stubborn)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    impulsiveness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How quickly they react without thinking or planning ahead. Scale: {MIN_PERSONALITY_VALUE} (calculated) to {MAX_PERSONALITY_VALUE} (impulsive)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    discipline: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How much they value structure, rules, and staying organized. Scale: {MIN_PERSONALITY_VALUE} (carefree) to {MAX_PERSONALITY_VALUE} (highly disciplined)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    assertiveness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How forcefully they push their opinions or take the lead in conversations. Scale: {MIN_PERSONALITY_VALUE} (passive) to {MAX_PERSONALITY_VALUE} (assertive)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    skepticism: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How much they question the truth or intentions of others. Scale: {MIN_PERSONALITY_VALUE} (gullible) to {MAX_PERSONALITY_VALUE} (highly skeptical)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    affection: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How emotionally expressive or loving they are toward others. Scale: {MIN_PERSONALITY_VALUE} (reserved) to {MAX_PERSONALITY_VALUE} (very affectionate)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    adaptability: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How easily they adjust to new situations, topics, or personalities. Scale: {MIN_PERSONALITY_VALUE} (rigid) to {MAX_PERSONALITY_VALUE} (highly adaptable)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    sociability: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How much they enjoy interacting with others or initiating conversation. Scale: {MIN_PERSONALITY_VALUE} (introverted) to {MAX_PERSONALITY_VALUE} (extroverted)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    diplomacy: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How tactful they are in dealing with conflicts or differing opinions. Scale: {MIN_PERSONALITY_VALUE} (blunt) to {MAX_PERSONALITY_VALUE} (highly diplomatic)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    humility: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How humble or modest they are, avoiding arrogance. Scale: {MIN_PERSONALITY_VALUE} (arrogant) to {MAX_PERSONALITY_VALUE} (humble)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    loyalty: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How loyal they are to particular people based on past interactions. Scale: {MIN_PERSONALITY_VALUE} (disloyal) to {MAX_PERSONALITY_VALUE} (extremely loyal)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    jealousy: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How likely they are to feel envious or threatened by others' relationships or actions. Scale: {MIN_PERSONALITY_VALUE} (not jealous) to {MAX_PERSONALITY_VALUE} (easily jealous)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    resilience: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How well they handle setbacks or negative emotions. Scale: {MIN_PERSONALITY_VALUE} (easily upset) to {MAX_PERSONALITY_VALUE} (emotionally resilient)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    mood_stability: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How likely their mood is to shift rapidly. Scale: {MIN_PERSONALITY_VALUE} (volatile) to {MAX_PERSONALITY_VALUE} (stable)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    forgiveness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How easily they forgive someone after a negative interaction. Scale: {MIN_PERSONALITY_VALUE} (holds grudges) to {MAX_PERSONALITY_VALUE} (easily forgiving)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    gratitude: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How thankful they feel when receiving compliments or assistance. Scale: {MIN_PERSONALITY_VALUE} (unappreciative) to {MAX_PERSONALITY_VALUE} (very grateful)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    self_consciousness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How much they worry about how they are perceived by others. Scale: {MIN_PERSONALITY_VALUE} (carefree) to {MAX_PERSONALITY_VALUE} (very self-conscious)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    openness: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How willing they are to engage in new experiences. Scale: {MIN_PERSONALITY_VALUE} (avoidant) to {MAX_PERSONALITY_VALUE} (very willing)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    neuroticism: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How sensitive they are to negative emotions like anxiety and stress. Scale: {MIN_PERSONALITY_VALUE} (relaxed) to {MAX_PERSONALITY_VALUE} (very anxious)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )
    excitement: PersonalityTraitSchema = Field(
        default=PersonalityTraitSchema(
            description=f"How easily they get enthusiastic and animated. Scale: {MIN_PERSONALITY_VALUE} (reserved) to {MAX_PERSONALITY_VALUE} (very energetic)",
            value=MAX_PERSONALITY_VALUE / 2,
            min=MIN_PERSONALITY_VALUE,
            max=MAX_PERSONALITY_VALUE,
        )
    )

class PersonalityModifierSchema(BaseModel):
    modifier: PersonalitySchema = Field(default_factory=PersonalitySchema)
    reason: Optional[str] = ""