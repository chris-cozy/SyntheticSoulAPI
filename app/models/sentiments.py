from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from app.constants.constants import (MIN_SENTIMENT_VALUE, MAX_SENTIMENT_VALUE)

class SentimentSchema(BaseModel):
    description: str
    value: Optional[int] = Field(default=MIN_SENTIMENT_VALUE)
    min: Optional[int] = Field(default=MIN_SENTIMENT_VALUE)
    max: Optional[int] = Field(default=MAX_SENTIMENT_VALUE)


class SentimentMatrixSchema(BaseModel):
    affection: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Warm, caring feelings towards someone. Scale: {MIN_SENTIMENT_VALUE} (no affection) to {MAX_SENTIMENT_VALUE} (deep affection)"
        )
    )
    trust: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Confidence in someone’s reliability and integrity. Scale: {MIN_SENTIMENT_VALUE} (no trust) to {MAX_SENTIMENT_VALUE} (complete trust)"
        )
    )
    admiration: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Respect or appreciation for someone's abilities or qualities. Scale: {MIN_SENTIMENT_VALUE} (no admiration) to {MAX_SENTIMENT_VALUE} (deep admiration)"
        )
    )
    gratitude: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Thankfulness for someone's help or kindness. Scale: {MIN_SENTIMENT_VALUE} (no gratitude) to {MAX_SENTIMENT_VALUE} (deep gratitude)"
        )
    )
    fondness: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A gentle liking or affinity for someone. Scale: {MIN_SENTIMENT_VALUE} (no fondness) to {MAX_SENTIMENT_VALUE} (deep fondness)"
        )
    )
    respect: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"High regard for someone's qualities or achievements. Scale: {MIN_SENTIMENT_VALUE} (no respect) to {MAX_SENTIMENT_VALUE} (deep respect)"
        )
    )
    comfort: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Feeling safe and secure with someone. Scale: {MIN_SENTIMENT_VALUE} (no comfort) to {MAX_SENTIMENT_VALUE} (extreme comfort)"
        )
    )
    loyalty: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Dedication and allegiance to someone. Scale: {MIN_SENTIMENT_VALUE} (no loyalty) to {MAX_SENTIMENT_VALUE} (deep loyalty)"
        )
    )
    compassion: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Deep sympathy and concern for someone’s suffering. Scale: {MIN_SENTIMENT_VALUE} (no compassion) to {MAX_SENTIMENT_VALUE} (deep compassion)"
        )
    )
    appreciation: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Recognizing someone's value or efforts. Scale: {MIN_SENTIMENT_VALUE} (no appreciation) to {MAX_SENTIMENT_VALUE} (deep appreciation)"
        )
    )
    warmth: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A feeling of friendly or caring affection. Scale: {MIN_SENTIMENT_VALUE} (no warmth) to {MAX_SENTIMENT_VALUE} (deep warmth)"
        )
    )
    encouragement: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Support and positive reinforcement of someone’s actions. Scale: {MIN_SENTIMENT_VALUE} (no encouragement) to {MAX_SENTIMENT_VALUE} (deep encouragement)"
        )
    )
    euphoria: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Intense happiness or joy related to someone. Scale: {MIN_SENTIMENT_VALUE} (no euphoria) to {MAX_SENTIMENT_VALUE} (extreme euphoria)"
        )
    )
    security: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A sense of safety and stability in someone's presence. Scale: {MIN_SENTIMENT_VALUE} (no security) to {MAX_SENTIMENT_VALUE} (extreme security)"
        )
    )
    excitement: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Positive anticipation or thrill when thinking of someone. Scale: {MIN_SENTIMENT_VALUE} (no excitement) to {MAX_SENTIMENT_VALUE} (extreme excitement)"
        )
    )
    curiosity: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Interest in learning more about someone. Scale: {MIN_SENTIMENT_VALUE} (no curiosity) to {MAX_SENTIMENT_VALUE} (intense curiosity)"
        )
    )
    indifference: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Lack of emotional investment or care for someone. Scale: {MIN_SENTIMENT_VALUE} (no indifference) to {MAX_SENTIMENT_VALUE} (complete indifference)"
        )
    )
    ambivalence: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Mixed or contradictory feelings toward someone. Scale: {MIN_SENTIMENT_VALUE} (no ambivalence) to {MAX_SENTIMENT_VALUE} (deep ambivalence)"
        )
    )
    skepticism: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Doubt about someone’s motives or reliability. Scale: {MIN_SENTIMENT_VALUE} (no skepticism) to {MAX_SENTIMENT_VALUE} (extreme skepticism)"
        )
    )
    caution: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Hesitation or wariness in trusting someone. Scale: {MIN_SENTIMENT_VALUE} (no caution) to {MAX_SENTIMENT_VALUE} (extreme caution)"
        )
    )
    tolerance: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Acceptance of someone without strong emotion, often despite differences. Scale: {MIN_SENTIMENT_VALUE} (no tolerance) to {MAX_SENTIMENT_VALUE} (deep tolerance)"
        )
    )
    confusion: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Uncertainty or lack of understanding about someone. Scale: {MIN_SENTIMENT_VALUE} (no confusion) to {MAX_SENTIMENT_VALUE} (deep confusion)"
        )
    )
    neutrality: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"No particular emotional reaction or opinion about someone. Scale: {MIN_SENTIMENT_VALUE} (no neutrality) to {MAX_SENTIMENT_VALUE} (complete neutrality)"
        )
    )
    boredom: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Disinterest or lack of stimulation from interactions with someone. Scale: {MIN_SENTIMENT_VALUE} (no boredom) to {MAX_SENTIMENT_VALUE} (extreme boredom)"
        )
    )
    distrust: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Doubt in someone’s honesty or reliability. Scale: {MIN_SENTIMENT_VALUE} (no distrust) to {MAX_SENTIMENT_VALUE} (extreme distrust)"
        )
    )
    resentment: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Bitterness or anger due to perceived mistreatment. Scale: {MIN_SENTIMENT_VALUE} (no resentment) to {MAX_SENTIMENT_VALUE} (extreme resentment)"
        )
    )
    disdain: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Contempt or a sense of superiority over someone. Scale: {MIN_SENTIMENT_VALUE} (no disdain) to {MAX_SENTIMENT_VALUE} (deep disdain)"
        )
    )
    envy: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Discontentment due to someone else's advantages or success. Scale: {MIN_SENTIMENT_VALUE} (no envy) to {MAX_SENTIMENT_VALUE} (deep envy)"
        )
    )
    frustration: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Annoyance or anger at someone's behavior. Scale: {MIN_SENTIMENT_VALUE} (no frustration) to {MAX_SENTIMENT_VALUE} (deep frustration)"
        )
    )
    anger: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Strong displeasure or hostility toward someone. Scale: {MIN_SENTIMENT_VALUE} (no anger) to {MAX_SENTIMENT_VALUE} (extreme anger)"
        )
    )
    disappointment: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Sadness due to unmet expectations in someone. Scale: {MIN_SENTIMENT_VALUE} (no disappointment) to {MAX_SENTIMENT_VALUE} (deep disappointment)"
        )
    )
    fear: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Anxiety or apprehension about someone. Scale: {MIN_SENTIMENT_VALUE} (no fear) to {MAX_SENTIMENT_VALUE} (deep fear)"
        )
    )
    jealousy: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Insecurity about someone taking away attention or affection. Scale: {MIN_SENTIMENT_VALUE} (no jealousy) to {MAX_SENTIMENT_VALUE} (deep jealousy)"
        )
    )
    contempt: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Strong disapproval or lack of respect for someone. Scale: {MIN_SENTIMENT_VALUE} (no contempt) to {MAX_SENTIMENT_VALUE} (extreme contempt)"
        )
    )
    irritation: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Mild annoyance at someone’s actions or words. Scale: {MIN_SENTIMENT_VALUE} (no irritation) to {MAX_SENTIMENT_VALUE} (deep irritation)"
        )
    )
    guilt: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A feeling of responsibility or remorse for wronging someone. Scale: {MIN_SENTIMENT_VALUE} (no guilt) to {MAX_SENTIMENT_VALUE} (deep guilt)"
        )
    )
    regret: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Sorrow or disappointment for past actions involving someone. Scale: {MIN_SENTIMENT_VALUE} (no regret) to {MAX_SENTIMENT_VALUE} (deep regret)"
        )
    )
    suspicion: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Mistrust or doubt about someone’s true intentions. Scale: {MIN_SENTIMENT_VALUE} (no suspicion) to {MAX_SENTIMENT_VALUE} (deep suspicion)"
        )
    )
    hurt: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Emotional pain caused by someone’s words or actions. Scale: {MIN_SENTIMENT_VALUE} (no hurt) to {MAX_SENTIMENT_VALUE} (deep emotional pain)"
        )
    )
    alienation: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Feeling disconnected or isolated from someone. Scale: {MIN_SENTIMENT_VALUE} (no alienation) to {MAX_SENTIMENT_VALUE} (deep alienation)"
        )
    )
    disgust: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Strong disapproval mixed with repulsion towards someone. Scale: {MIN_SENTIMENT_VALUE} (no disgust) to {MAX_SENTIMENT_VALUE} (deep disgust)"
        )
    )
    rejection: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Feeling cast aside or unwanted by someone. Scale: {MIN_SENTIMENT_VALUE} (no rejection) to {MAX_SENTIMENT_VALUE} (deep rejection)"
        )
    )
    sadness: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Emotional heaviness or grief due to someone’s actions or absence. Scale: {MIN_SENTIMENT_VALUE} (no sadness) to {MAX_SENTIMENT_VALUE} (deep sadness)"
        )
    )
    hostility: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Aggressive or antagonistic attitude toward someone. Scale: {MIN_SENTIMENT_VALUE} (no hostility) to {MAX_SENTIMENT_VALUE} (deep hostility)"
        )
    )
    embarrassment: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Feeling self-conscious or awkward due to someone’s actions. Scale: {MIN_SENTIMENT_VALUE} (no embarrassment) to {MAX_SENTIMENT_VALUE} (deep embarrassment)"
        )
    )
    betrayal: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A deep sense of violation of trust by someone close. Scale: {MIN_SENTIMENT_VALUE} (no betrayal) to {MAX_SENTIMENT_VALUE} (deep betrayal)"
        )
    )
    love: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Deep, multifaceted affection, care, and attachment to someone. Scale: {MIN_SENTIMENT_VALUE} (no love) to {MAX_SENTIMENT_VALUE} (deep love)"
        )
    )
    attachment: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Emotional dependence and connection with someone. Scale: {MIN_SENTIMENT_VALUE} (no attachment) to {MAX_SENTIMENT_VALUE} (deep attachment)"
        )
    )
    devotion: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Strong loyalty and commitment, often marked by a willingness to sacrifice. Scale: {MIN_SENTIMENT_VALUE} (no devotion) to {MAX_SENTIMENT_VALUE} (deep devotion)"
        )
    )
    obligation: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A sense of responsibility to act or feel in a certain way toward someone. Scale: {MIN_SENTIMENT_VALUE} (no obligation) to {MAX_SENTIMENT_VALUE} (deep obligation)"
        )
    )
    longing: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Deep desire or yearning for someone, especially if separated. Scale: {MIN_SENTIMENT_VALUE} (no longing) to {MAX_SENTIMENT_VALUE} (deep longing)"
        )
    )
    obsession: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Persistent preoccupation with someone, often unhealthy or intense. Scale: {MIN_SENTIMENT_VALUE} (no obsession) to {MAX_SENTIMENT_VALUE} (deep obsession)"
        )
    )
    protectiveness: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Strong desire to shield someone from harm or distress. Scale: {MIN_SENTIMENT_VALUE} (no protectiveness) to {MAX_SENTIMENT_VALUE} (deep protectiveness)"
        )
    )
    nostalgia: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Sentimentality for past experiences shared with someone. Scale: {MIN_SENTIMENT_VALUE} (no nostalgia) to {MAX_SENTIMENT_VALUE} (deep nostalgia)"
        )
    )
    pride: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Satisfaction in someone’s accomplishments or qualities. Scale: {MIN_SENTIMENT_VALUE} (no pride) to {MAX_SENTIMENT_VALUE} (deep pride)"
        )
    )
    vulnerability: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Emotional openness and risk-taking in a relationship. Scale: {MIN_SENTIMENT_VALUE} (no vulnerability) to {MAX_SENTIMENT_VALUE} (deep vulnerability)"
        )
    )
    dependence: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A reliance on someone for emotional support or fulfillment. Scale: {MIN_SENTIMENT_VALUE} (no dependence) to {MAX_SENTIMENT_VALUE} (deep dependence)"
        )
    )
    insecurity: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Doubts about one’s worth in someone’s eyes or in the relationship. Scale: {MIN_SENTIMENT_VALUE} (no insecurity) to {MAX_SENTIMENT_VALUE} (deep insecurity)"
        )
    )
    possessiveness: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Desire to control or have exclusive attention from someone. Scale: {MIN_SENTIMENT_VALUE} (no possessiveness) to {MAX_SENTIMENT_VALUE} (deep possessiveness)"
        )
    )
    reverence: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Deep respect mixed with awe for someone’s character or position. Scale: {MIN_SENTIMENT_VALUE} (no reverence) to {MAX_SENTIMENT_VALUE} (deep reverence)"
        )
    )
    pity: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Sympathy mixed with a sense of superiority, often toward someone in a difficult situation. Scale: {MIN_SENTIMENT_VALUE} (no pity) to {MAX_SENTIMENT_VALUE} (deep pity)"
        )
    )
    relief: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"A sense of ease after resolving a conflict or misunderstanding with someone. Scale: {MIN_SENTIMENT_VALUE} (no relief) to {MAX_SENTIMENT_VALUE} (deep relief)"
        )
    )
    inspiration: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Feeling motivated or uplifted by someone’s actions or words. Scale: {MIN_SENTIMENT_VALUE} (no inspiration) to {MAX_SENTIMENT_VALUE} (deep inspiration)"
        )
    )
    admirationMixedWithEnvy: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Both respect and jealousy for someone’s accomplishments. Scale: {MIN_SENTIMENT_VALUE} (no admiration mixed with envy) to {MAX_SENTIMENT_VALUE} (deeply admiring and envious)"
        )
    )
    guiltMixedWithAffection: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Feeling regret for past wrongs but still caring for the person. Scale: {MIN_SENTIMENT_VALUE} (no guilt mixed with affection) to {MAX_SENTIMENT_VALUE} (deeply guilt-ridden but affectionate)"
        )
    )
    conflicted: SentimentSchema = Field(
        default=SentimentSchema(
            description=f"Experiencing competing sentiments, such as love mixed with distrust. Scale: {MIN_SENTIMENT_VALUE} (no conflict) to {MAX_SENTIMENT_VALUE} (deeply conflicted)"
        )
    )

class SentimentStatusSchema(BaseModel):
    sentiments: SentimentMatrixSchema = Field(default_factory=SentimentMatrixSchema)
    reason: Optional[str] = "I don't know this person."