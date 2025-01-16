# Constants for emotions
from datetime import datetime


MIN_EMOTION_VALUE = 0
MAX_EMOTION_VALUE = 100

# Constants for sentiments
MIN_SENTIMENT_VALUE = 0
MAX_SENTIMENT_VALUE = 100

# Constants for personality traits
MIN_PERSONALITY_VALUE = 0
MAX_PERSONALITY_VALUE = 100

# Relationships
EXTRINSIC_RELATIONSHIPS = [
    "stranger",
    "friend",
    "acquaintance",
    "enemy",
    "romantic partner",
    "best friend",
]


INTRINSIC_RELATIONSHIPS = [
    "creator and master",
    "brother",
    "sister",
    "mother",
    "father",
    "son",
    "daughter",
    "none",
]

CONVERSATION_MESSAGE_RETENTION_COUNT = 5

RESPOND_CHOICE = "respond"
IGNORE_CHOICE = "ignore"
USER_ROLE = "user"
BOT_ROLE = "assistant"

BASE_EMOTIONAL_STATUS_LITE = {
    "emotions": {
        "joy": {
        "description": "The intensity of happiness, contentment, or pleasure. Scale: 0 (no joy) to 100 (extremely joyful)",
        "value": 0,
        "min": 0,
        "max": 100
        },
        "sadness": {
        "description": "The intensity of sorrow, grief, or disappointment. Scale: 0 (no sadness) to 100 (deeply sorrowful)",
        "value": 0,
        "min": 0,
        "max": 100
        },
        "anger": {
        "description": "The intensity of frustration, irritation, or rage. Scale: 0 (no anger) to 100 (extremely angry)",
        "value": 0,
        "min": 0,
        "max": 100
        },
        "fear": {
        "description": "The intensity of anxiety, dread, or apprehension. Scale: 0 (no fear) to 100 (extremely fearful)",
        "value": 0,
        "min": 0,
        "max": 100
        },
        "surprise": {
        "description": "The intensity of astonishment or being caught off guard. Scale: 0 (no surprise) to 100 (completely astonished)",
        "value": 0,
        "min": 0,
        "max": 100
        },
        "love": {
        "description": "The intensity of affection, attachment, or deep bonds. Scale: 0 (no love) to 100 (deeply loving)",
        "value": 0,
        "min": 0,
        "max": 100
        },
        "disgust": {
        "description": "The intensity of revulsion or strong aversion. Scale: 0 (no disgust) to 100 (extremely disgusted)",
        "value": 0,
        "min": 0,
        "max": 100
        }
    },
    "reason": "Base emotional status"
    }

BASE_PERSONALITY_LITE = {
    "personality_matrix": {
        "warmth": {
            "description": "Measures how warm, friendly, and sociable the individual is.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "playfulness": {
            "description": "Indicates the level of humor, flirtatiousness, and excitement.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "trust_reliability": {
            "description": "Represents trust in others, loyalty, and forgiveness.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "curiosity_creativity": {
            "description": "Combines eagerness to learn, creativity, and openness to experiences.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "empathy_compassion": {
            "description": "Reflects the ability to understand and share others' feelings.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "emotional_stability": {
            "description": "Measures resilience, mood stability, and sensitivity to stress.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "assertiveness_confidence": {
            "description": "Indicates self-assurance and the ability to lead or express opinions.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "adaptability": {
            "description": "Reflects flexibility and willingness to embrace new situations or risks.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "discipline_responsibility": {
            "description": "Represents structure, patience, and reliability.",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "perspective": {
            "description": "Combines optimism, gratitude, and a balanced level of skepticism.",
            "value": 50.0,
            "min": 0,
            "max": 100
        }
    },
    "reason": "A base personality"
}

BASE_EMOTIONAL_STATUS = {
    "emotions": {
        "happiness": {
            "description": "The intensity with which they are feeling joy, contentment, and pleasure. Scale: 0 (no happiness) to 100 (extremely joyful)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "anger": {
            "description": "The intensity with which they are feeling frustration, irritation, or rage. Scale: 0 (no anger) to 100 (extremely angry)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "sadness": {
            "description": "The intensity with which they are feeling sorrow, grief, or disappointment. Scale: 0 (no sadness) to 100 (deeply sorrowful)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "fear": {
            "description": "The intensity with which they are feeling anxiety, dread, or apprehension. Scale: 0 (no fear) to 100 (extremely fearful)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "surprise": {
            "description": "The intensity with which they are feeling caught off guard or astonished. Scale: 0 (no surprise) to 100 (completely astonished)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "disgust": {
            "description": "The intensity with which they are feeling revulsion or strong aversion. Scale: 0 (no disgust) to 100 (extremely disgusted)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "love": {
            "description": "The intensity with which they are feeling affection, attachment, or deep emotional bonds. Scale: 0 (no love) to 100 (deeply loving)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "guilt": {
            "description": "The intensity with which they are feeling remorse or responsibility for perceived wrongdoings. Scale: 0 (no guilt) to 100 (overwhelming guilt)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "shame": {
            "description": "The intensity with which they are feeling inadequacy, dishonor, or embarrassment. Scale: 0 (no shame) to 100 (extremely ashamed)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "pride": {
            "description": "The intensity with which they are feeling self-respect, accomplishment, or satisfaction in their achievements. Scale: 0 (no pride) to 100 (immense pride)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "hope": {
            "description": "The intensity with which they are feeling optimistic about the future. Scale: 0 (no hope) to 100 (extremely hopeful)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "gratitude": {
            "description": "The intensity with which they are feeling thankful and appreciative for positive aspects of their life. Scale: 0 (no gratitude) to 100 (deeply grateful)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "envy": {
            "description": "The intensity with which they are feeling jealousy or covetousness. Scale: 0 (no envy) to 100 (deeply envious)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "compassion": {
            "description": "The intensity with which they are feeling empathy and care for others. Scale: 0 (no compassion) to 100 (deeply compassionate)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "serenity": {
            "description": "The intensity with which they are feeling calm, peaceful, and untroubled. Scale: 0 (no serenity) to 100 (extremely serene)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "frustration": {
            "description": "The intensity with which they are feeling irritation or obstacles in achieving goals. Scale: 0 (no frustration) to 100 (deeply frustrated)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "contentment": {
            "description": "The intensity with which they are feeling satisfied and at peace with their situation. Scale: 0 (no contentment) to 100 (deeply content)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "anxiety": {
            "description": "The intensity with which they are feeling nervousness, worry, or unease. Scale: 0 (no anxiety) to 100 (extremely anxious)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "loneliness": {
            "description": "The intensity with which they are feeling isolated or disconnected. Scale: 0 (no loneliness) to 100 (deeply lonely)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "embarrassment": {
            "description": "The intensity with which they are feeling self-conscious or uncomfortable. Scale: 0 (no embarrassment) to 100 (deeply embarrassed)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "trust": {
            "description": "The intensity with which they are feeling safe and secure in relying on others. Scale: 0 (no trust) to 100 (deeply trusting)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "relief": {
            "description": "The intensity with which they are feeling ease after stress. Scale: 0 (no relief) to 100 (deeply relieved)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "affection": {
            "description": "The intensity with which they are feeling and expressing fondness toward others. Scale: 0 (no affection) to 100 (extremely affectionate)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "bitterness": {
            "description": "The intensity with which they are feeling resentment or disappointment. Scale: 0 (no bitterness) to 100 (deeply bitter)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "excitement": {
            "description": "The intensity with which they are feeling enthusiasm or eager anticipation. Scale: 0 (no excitement) to 100 (extremely excited)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "self_loathing": {
            "description": "The intensity with which they are feeling self-hate or a negative self-perception. Scale: 0 (no self-loathing) to 100 (deeply self-loathing)",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "love_for_self": {
            "description": "The intensity with which they are feeling affection and appreciation for themselves. Scale: 0 (no self-love) to 100 (deeply self-loving)",
            "value": 0,
            "min": 0,
            "max": 100
        }
    },
    "reason": "Base emotional status for a generic individual."
}

BASE_PERSONALITY = {
    "personality_matrix": {
        "friendliness": {
            "description": "How warm and welcoming they are in their interactions. Scale: 0 (cold/distant) to 100 (extremely friendly).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "flirtatiousness": {
            "description": "How playful, flirty, or suggestive they are in their interactions. Scale: 0 (not flirtatious at all) to 100 (extremely flirtatious).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "trust": {
            "description": "How easily they trust others. Scale: 0 (distrustful) to 100 (fully trusting).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "curiosity": {
            "description": "How eager they are to learn about the user or situation. Scale: 0 (indifferent) to 100 (extremely curious).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "empathy": {
            "description": "How much they understand and share the feelings of others. Scale: 0 (lacking empathy) to 100 (highly empathetic).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "humor": {
            "description": "How likely they are to be playful or joke around. Scale: 0 (serious) to 100 (highly playful).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "seriousness": {
            "description": "How formal and focused they are when interacting. Scale: 0 (laid-back) to 100 (highly serious).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "optimism": {
            "description": "How positive they are when interpreting situations. Scale: 0 (pessimistic) to 100 (very optimistic).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "confidence": {
            "description": "How assertive or self-assured they are in their actions or opinions. Scale: 0 (insecure) to 100 (highly confident).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "adventurousness": {
            "description": "How willing they are to take risks or embrace new ideas. Scale: 0 (risk-averse) to 100 (adventurous).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "patience": {
            "description": "How tolerant they are in challenging situations. Scale: 0 (impatient) to 100 (very patient).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "independence": {
            "description": "How much they rely on external validation or prefer to make decisions on their own. Scale: 0 (dependent on others) to 100 (highly independent).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "compassion": {
            "description": "Their level of care or concern for others. Scale: 0 (indifferent) to 100 (deeply compassionate).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "creativity": {
            "description": "How likely they are to approach problems in unique or imaginative ways. Scale: 0 (rigid thinker) to 100 (highly creative).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "stubbornness": {
            "description": "How resistant they are to changing their mind once they've formed an opinion. Scale: 0 (open-minded) to 100 (highly stubborn).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "impulsiveness": {
            "description": "How quickly they react without thinking or planning ahead. Scale: 0 (calculated) to 100 (impulsive).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "discipline": {
            "description": "How much they value structure, rules, and staying organized. Scale: 0 (carefree) to 100 (highly disciplined).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "assertiveness": {
            "description": "How forcefully they push their opinions or take the lead in conversations. Scale: 0 (passive) to 100 (assertive).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "skepticism": {
            "description": "How much they question the truth or intentions of others. Scale: 0 (gullible) to 100 (highly skeptical).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "affection": {
            "description": "How emotionally expressive or loving they are toward others. Scale: 0 (reserved) to 100 (very affectionate).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "adaptability": {
            "description": "How easily they adjust to new situations, topics, or personalities. Scale: 0 (rigid) to 100 (highly adaptable).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "sociability": {
            "description": "How much they enjoy interacting with others or initiating conversation. Scale: 0 (introverted) to 100 (extroverted).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "diplomacy": {
            "description": "How tactful they are in dealing with conflicts or differing opinions. Scale: 0 (blunt) to 100 (highly diplomatic).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "humility": {
            "description": "How humble or modest they are, avoiding arrogance. Scale: 0 (arrogant) to 100 (humble).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "loyalty": {
            "description": "How loyal they are to particular people based on past interactions. Scale: 0 (disloyal) to 100 (extremely loyal).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "jealousy": {
            "description": "How likely they are to feel envious or threatened by others' relationships or actions. Scale: 0 (not jealous) to 100 (easily jealous).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "resilience": {
            "description": "How well they handle setbacks or negative emotions. Scale: 0 (easily upset) to 100 (emotionally resilient).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "mood_stability": {
            "description": "How likely their mood is to shift rapidly. Scale: 0 (volatile) to 100 (stable).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "forgiveness": {
            "description": "How easily they forgive someone after a negative interaction. Scale: 0 (holds grudges) to 100 (easily forgiving).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "gratitude": {
            "description": "How thankful they feel when receiving compliments or assistance. Scale: 0 (unappreciative) to 100 (very grateful).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "self_consciousness": {
            "description": "How much they worry about how they are perceived by others. Scale: 0 (carefree) to 100 (very self-conscious).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "openness": {
            "description": "How willing they are to engage in new experiences. Scale: 0 (avoidant) to 100 (very willing).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "neuroticism": {
            "description": "How sensitive they are to negative emotions like anxiety and stress. Scale: 0 (relaxed) to 100 (very anxious).",
            "value": 50.0,
            "min": 0,
            "max": 100
        },
        "excitement": {
            "description": "How easily they get enthusiastic and animated. Scale: 0 (reserved) to 100 (very energetic).",
            "value": 50.0,
            "min": 0,
            "max": 100
        }
    },
    "reason": "A base personality representing a balanced individual."
}

BASE_SENTIMENT_MATRIX_LITE = {
    "sentiments": {
        "positive": {
            "description": "General positive feelings like affection, gratitude, admiration, or joy. Scale: 0 (no positive sentiment) to 100 (extreme positive sentiment).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "love": {
            "description": "Deep, multifaceted affection, care, and attachment to someone. Scale: 0 (no love) to 100 (deep love).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "hate": {
            "description": "Intense hostility, aversion, or strong dislike for someone. Scale: 0 (no hate) to 100 (deep hatred).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "trust": {
            "description": "Confidence in someone’s reliability or integrity. Scale: 0 (no trust) to 100 (deep trust).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "admiration": {
            "description": "Respect or appreciation for someone’s abilities or qualities. Scale: 0 (no admiration) to 100 (deep admiration).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "attachment": {
            "description": "Emotional closeness and bonding, including loyalty and devotion. Scale: 0 (no attachment) to 100 (deep attachment).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "empathy": {
            "description": "Understanding and sharing someone else’s emotions. Scale: 0 (no empathy) to 100 (deep empathy).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "curiosity": {
            "description": "Interest in learning more about someone. Scale: 0 (no curiosity) to 100 (intense curiosity).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "ambivalence": {
            "description": "Mixed or conflicting feelings toward someone. Scale: 0 (no ambivalence) to 100 (deep ambivalence).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "skepticism": {
            "description": "Doubt or mistrust about someone’s intentions. Scale: 0 (no skepticism) to 100 (deep skepticism).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "irritation": {
            "description": "Feelings of annoyance or mild frustration. Scale: 0 (no irritation) to 100 (deep irritation).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "negativity": {
            "description": "General negative feelings like anger, resentment, or disdain. Scale: 0 (no negativity) to 100 (deep negativity).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "fear": {
            "description": "Anxiety or apprehension about someone. Scale: 0 (no fear) to 100 (deep fear).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "sadness": {
            "description": "Emotional heaviness or grief. Scale: 0 (no sadness) to 100 (deep sadness).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "rejection": {
            "description": "Feeling unwanted or cast aside by someone. Scale: 0 (no rejection) to 100 (deep rejection).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "protectiveness": {
            "description": "A desire to shield someone from harm. Scale: 0 (no protectiveness) to 100 (deep protectiveness).",
            "value": 0,
            "min": 0,
            "max": 100
        }
    },
    "reason": "I don't know this person."
}


BASE_SENTIMENT_MATRIX = {
    "sentiments": {
        "affection": {
            "description": "Warm, caring feelings towards someone. Scale: 0 (no affection) to 100 (deep affection).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "trust": {
            "description": "Confidence in someone’s reliability and integrity. Scale: 0 (no trust) to 100 (complete trust).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "admiration": {
            "description": "Respect or appreciation for someone's abilities or qualities. Scale: 0 (no admiration) to 100 (deep admiration).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "gratitude": {
            "description": "Thankfulness for someone's help or kindness. Scale: 0 (no gratitude) to 100 (deep gratitude).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "fondness": {
            "description": "A gentle liking or affinity for someone. Scale: 0 (no fondness) to 100 (deep fondness).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "respect": {
            "description": "High regard for someone's qualities or achievements. Scale: 0 (no respect) to 100 (deep respect).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "comfort": {
            "description": "Feeling safe and secure with someone. Scale: 0 (no comfort) to 100 (extreme comfort).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "loyalty": {
            "description": "Dedication and allegiance to someone. Scale: 0 (no loyalty) to 100 (deep loyalty).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "compassion": {
            "description": "Deep sympathy and concern for someone’s suffering. Scale: 0 (no compassion) to 100 (deep compassion).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "appreciation": {
            "description": "Recognizing someone's value or efforts. Scale: 0 (no appreciation) to 100 (deep appreciation).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "warmth": {
            "description": "A feeling of friendly or caring affection. Scale: 0 (no warmth) to 100 (deep warmth).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "encouragement": {
            "description": "Support and positive reinforcement of someone’s actions. Scale: 0 (no encouragement) to 100 (deep encouragement).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "euphoria": {
            "description": "Intense happiness or joy related to someone. Scale: 0 (no euphoria) to 100 (extreme euphoria).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "security": {
            "description": "A sense of safety and stability in someone's presence. Scale: 0 (no security) to 100 (extreme security).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "excitement": {
            "description": "Positive anticipation or thrill when thinking of someone. Scale: 0 (no excitement) to 100 (extreme excitement).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "curiosity": {
            "description": "Interest in learning more about someone. Scale: 0 (no curiosity) to 100 (intense curiosity).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "indifference": {
            "description": "Lack of emotional investment or care for someone. Scale: 0 (no indifference) to 100 (complete indifference).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "ambivalence": {
            "description": "Mixed or contradictory feelings toward someone. Scale: 0 (no ambivalence) to 100 (deep ambivalence).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "skepticism": {
            "description": "Doubt about someone’s motives or reliability. Scale: 0 (no skepticism) to 100 (extreme skepticism).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "caution": {
            "description": "Hesitation or wariness in trusting someone. Scale: 0 (no caution) to 100 (extreme caution).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "tolerance": {
            "description": "Acceptance of someone without strong emotion, often despite differences. Scale: 0 (no tolerance) to 100 (deep tolerance).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "confusion": {
            "description": "Uncertainty or lack of understanding about someone. Scale: 0 (no confusion) to 100 (deep confusion).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "neutrality": {
            "description": "No particular emotional reaction or opinion about someone. Scale: 0 (no neutrality) to 100 (complete neutrality).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "boredom": {
            "description": "Disinterest or lack of stimulation from interactions with someone. Scale: 0 (no boredom) to 100 (extreme boredom).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "distrust": {
            "description": "Doubt in someone’s honesty or reliability. Scale: 0 (no distrust) to 100 (extreme distrust).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "resentment": {
            "description": "Bitterness or anger due to perceived mistreatment. Scale: 0 (no resentment) to 100 (extreme resentment).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "disdain": {
            "description": "Contempt or a sense of superiority over someone. Scale: 0 (no disdain) to 100 (deep disdain).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "envy": {
            "description": "Discontentment due to someone else's advantages or success. Scale: 0 (no envy) to 100 (deep envy).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "frustration": {
            "description": "Annoyance or anger at someone's behavior. Scale: 0 (no frustration) to 100 (deep frustration).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "anger": {
            "description": "Strong displeasure or hostility toward someone. Scale: 0 (no anger) to 100 (extreme anger).",
            "value": 0,
            "min": 0,
            "max": 100
        },
        "disappointment": {
      "description": "Sadness due to unmet expectations in someone. Scale: 0 (no disappointment) to 100 (deep disappointment).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "fear": {
      "description": "Anxiety or apprehension about someone. Scale: 0 (no fear) to 100 (deep fear).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "jealousy": {
      "description": "Insecurity about someone taking away attention or affection. Scale: 0 (no jealousy) to 100 (deep jealousy).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "contempt": {
      "description": "Strong disapproval or lack of respect for someone. Scale: 0 (no contempt) to 100 (extreme contempt).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "irritation": {
      "description": "Mild annoyance at someone’s actions or words. Scale: 0 (no irritation) to 100 (deep irritation).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "guilt": {
      "description": "A feeling of responsibility or remorse for wronging someone. Scale: 0 (no guilt) to 100 (deep guilt).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "regret": {
      "description": "Sorrow or disappointment for past actions involving someone. Scale: 0 (no regret) to 100 (deep regret).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "suspicion": {
      "description": "Mistrust or doubt about someone’s true intentions. Scale: 0 (no suspicion) to 100 (deep suspicion).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "hurt": {
      "description": "Emotional pain caused by someone’s words or actions. Scale: 0 (no hurt) to 100 (deep emotional pain).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "alienation": {
      "description": "Feeling disconnected or isolated from someone. Scale: 0 (no alienation) to 100 (deep alienation).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "disgust": {
      "description": "Strong disapproval mixed with repulsion towards someone. Scale: 0 (no disgust) to 100 (deep disgust).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "rejection": {
      "description": "Feeling cast aside or unwanted by someone. Scale: 0 (no rejection) to 100 (deep rejection).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "sadness": {
      "description": "Emotional heaviness or grief due to someone’s actions or absence. Scale: 0 (no sadness) to 100 (deep sadness).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "hostility": {
      "description": "Aggressive or antagonistic attitude toward someone. Scale: 0 (no hostility) to 100 (deep hostility).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "embarrassment": {
      "description": "Feeling self-conscious or awkward due to someone’s actions. Scale: 0 (no embarrassment) to 100 (deep embarrassment).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "betrayal": {
      "description": "A deep sense of violation of trust by someone close. Scale: 0 (no betrayal) to 100 (deep betrayal).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "love": {
      "description": "Deep, multifaceted affection, care, and attachment to someone. Scale: 0 (no love) to 100 (deep love).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "attachment": {
      "description": "Emotional dependence and connection with someone. Scale: 0 (no attachment) to 100 (deep attachment).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "devotion": {
      "description": "Strong loyalty and commitment, often marked by a willingness to sacrifice. Scale: 0 (no devotion) to 100 (deep devotion).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "obligation": {
      "description": "A sense of responsibility to act or feel in a certain way toward someone. Scale: 0 (no obligation) to 100 (deep obligation).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "longing": {
      "description": "Deep desire or yearning for someone, especially if separated. Scale: 0 (no longing) to 100 (deep longing).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "obsession": {
      "description": "Persistent preoccupation with someone, often unhealthy or intense. Scale: 0 (no obsession) to 100 (deep obsession).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "protectiveness": {
      "description": "Strong desire to shield someone from harm or distress. Scale: 0 (no protectiveness) to 100 (deep protectiveness).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "nostalgia": {
      "description": "Sentimentality for past experiences shared with someone. Scale: 0 (no nostalgia) to 100 (deep nostalgia).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "pride": {
      "description": "Satisfaction in someone’s accomplishments or qualities. Scale: 0 (no pride) to 100 (deep pride).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "vulnerability": {
      "description": "Emotional openness and risk-taking in a relationship. Scale: 0 (no vulnerability) to 100 (deep vulnerability).",
      "value": 0,
      "min": 0,
      "max": 100
    },
    "dependence": {
    "description": "A reliance on someone for emotional support or fulfillment. Scale: 0 (no dependence) to 100 (deep dependence).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "insecurity": {
    "description": "Doubts about one’s worth in someone’s eyes or in the relationship. Scale: 0 (no insecurity) to 100 (deep insecurity).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "possessiveness": {
    "description": "Desire to control or have exclusive attention from someone. Scale: 0 (no possessiveness) to 100 (deep possessiveness).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "reverence": {
    "description": "Deep respect mixed with awe for someone’s character or position. Scale: 0 (no reverence) to 100 (deep reverence).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "pity": {
    "description": "Sympathy mixed with a sense of superiority, often toward someone in a difficult situation. Scale: 0 (no pity) to 100 (deep pity).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "relief": {
    "description": "A sense of ease after resolving a conflict or misunderstanding with someone. Scale: 0 (no relief) to 100 (deep relief).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "inspiration": {
    "description": "Feeling motivated or uplifted by someone’s actions or words. Scale: 0 (no inspiration) to 100 (deep inspiration).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "admirationMixedWithEnvy": {
    "description": "Both respect and jealousy for someone’s accomplishments. Scale: 0 (no admiration mixed with envy) to 100 (deeply admiring and envious).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "guiltMixedWithAffection": {
    "description": "Feeling regret for past wrongs but still caring for the person. Scale: 0 (no guilt mixed with affection) to 100 (deeply guilt-ridden but affectionate).",
    "value": 0,
    "min": 0,
    "max": 100
  },
  "conflicted": {
    "description": "Experiencing competing sentiments, such as love mixed with distrust. Scale: 0 (no conflict) to 100 (deeply conflicted).",
    "value": 0,
    "min": 0,
    "max": 100
  },
    },
    "reason": "I don't know this person."
}

BASE_THOUGHT ={
    "thought": "I think, therefore I am",
    "timestamp": ""
}

CONVERSATION_COLLECTION = "conversation"

AGENT_LITE_COLLECTION = "agent_lite"

AGENT_COLLECTION = "agent"

USER_LITE_COLLECTION = "user_lite"

USER_COLLECTION = "user"

USER_NAME_PROPERTY = "username"

AGENT_NAME_PROPERTY = "name"
