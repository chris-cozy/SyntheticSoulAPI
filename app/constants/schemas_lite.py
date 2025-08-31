
from app.constants.constants import MAX_EMOTION_VALUE, MAX_PERSONALITY_VALUE, MAX_SENTIMENT_VALUE, MIN_EMOTION_VALUE, MIN_PERSONALITY_VALUE, MIN_SENTIMENT_VALUE

def get_personality_status_schema_lite():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "personality_status_response",
            "schema": {
                "type": "object",
                "properties": {
                    "warmth": {
                        "description": f"Measures how warm, friendly, and sociable the individual is. Scale: {MIN_PERSONALITY_VALUE} (cold/distant) to {MAX_PERSONALITY_VALUE} (extremely warm and sociable)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of warmth. Scale: {MIN_PERSONALITY_VALUE} (cold/distant) to {MAX_PERSONALITY_VALUE} (extremely warm and sociable)",
                                "type": "number",
                            },
                        },
                    },
                    "playfulness": {
                        "description": f"Indicates the level of humor, flirtatiousness, and excitement. Scale: {MIN_PERSONALITY_VALUE} (serious/reserved) to {MAX_PERSONALITY_VALUE} (extremely playful and energetic)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of playfulness. Scale: {MIN_PERSONALITY_VALUE} (serious/reserved) to {MAX_PERSONALITY_VALUE} (extremely playful and energetic)",
                                "type": "number",
                            },
                        },
                    },
                    "trust_reliability": {
                        "description": f"Represents trust in others, loyalty, and forgiveness. Scale: {MIN_PERSONALITY_VALUE} (distrustful/disloyal) to {MAX_PERSONALITY_VALUE} (fully trusting and reliable)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of trust and reliability. Scale: {MIN_PERSONALITY_VALUE} (distrustful/disloyal) to {MAX_PERSONALITY_VALUE} (fully trusting and reliable)",
                                "type": "number",
                            },
                        },
                    },
                    "curiosity_creativity": {
                        "description": f"Combines eagerness to learn, creativity, and openness to experiences. Scale: {MIN_PERSONALITY_VALUE} (indifferent/rigid thinker) to {MAX_PERSONALITY_VALUE} (extremely curious and creative)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of curiosity and creativity. Scale: {MIN_PERSONALITY_VALUE} (indifferent/rigid thinker) to {MAX_PERSONALITY_VALUE} (extremely curious and creative)",
                                "type": "number",
                            },
                        },
                    },
                    "empathy_compassion": {
                        "description": f"Reflects the ability to understand and share others' feelings. Scale: {MIN_PERSONALITY_VALUE} (lacking empathy/indifferent) to {MAX_PERSONALITY_VALUE} (highly empathetic and compassionate)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of empathy and compassion. Scale: {MIN_PERSONALITY_VALUE} (lacking empathy/indifferent) to {MAX_PERSONALITY_VALUE} (highly empathetic and compassionate)",
                                "type": "number",
                            },
                        },
                    },
                    "emotional_stability": {
                        "description": f"Measures resilience, mood stability, and sensitivity to stress. Scale: {MIN_PERSONALITY_VALUE} (emotionally volatile) to {MAX_PERSONALITY_VALUE} (extremely stable and resilient)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of emotional stability. Scale: {MIN_PERSONALITY_VALUE} (emotionally volatile) to {MAX_PERSONALITY_VALUE} (extremely stable and resilient)",
                                "type": "number",
                            },
                        },
                    },
                    "assertiveness_confidence": {
                        "description": f"Indicates self-assurance and the ability to lead or express opinions. Scale: {MIN_PERSONALITY_VALUE} (passive/insecure) to {MAX_PERSONALITY_VALUE} (highly assertive and confident)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of assertiveness and confidence. Scale: {MIN_PERSONALITY_VALUE} (passive/insecure) to {MAX_PERSONALITY_VALUE} (highly assertive and confident)",
                                "type": "number",
                            },
                        },
                    },
                    "adaptability": {
                        "description": f"Reflects flexibility and willingness to embrace new situations or risks. Scale: {MIN_PERSONALITY_VALUE} (rigid) to {MAX_PERSONALITY_VALUE} (highly adaptable and flexible)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of adaptability. Scale: {MIN_PERSONALITY_VALUE} (rigid) to {MAX_PERSONALITY_VALUE} (highly adaptable and flexible)",
                                "type": "number",
                            },
                        },
                    },
                    "discipline_responsibility": {
                        "description": f"Represents structure, patience, and reliability. Scale: {MIN_PERSONALITY_VALUE} (carefree/disorganized) to {MAX_PERSONALITY_VALUE} (highly disciplined and responsible)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of discipline and responsibility. Scale: {MIN_PERSONALITY_VALUE} (carefree/disorganized) to {MAX_PERSONALITY_VALUE} (highly disciplined and responsible)",
                                "type": "number",
                            },
                        },
                    },
                    "perspective": {
                        "description": f"Combines optimism, gratitude, and a balanced level of skepticism. Scale: {MIN_PERSONALITY_VALUE} (pessimistic/ungrateful) to {MAX_PERSONALITY_VALUE} (highly positive and balanced)",
                        "type": "object",
                        "properties": {
                            "value": {
                                "description": f"The intensity of perspective. Scale: {MIN_PERSONALITY_VALUE} (pessimistic/ungrateful) to {MAX_PERSONALITY_VALUE} (highly positive and balanced)",
                                "type": "number",
                            },
                        },
                    },
                },
                "additionalProperties": False,
            },
        },
    }

def get_emotion_status_schema_lite():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "emotion_status_response",
            "schema": {
                "type": "object",
                "properties": {
                    "emotions": {
                        "type": "object",
                        "properties": {
                            "joy": {
                                "description": f"The intensity of happiness, contentment, or pleasure. Scale: {MIN_EMOTION_VALUE} (no joy) to {MAX_EMOTION_VALUE} (extremely joyful)",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"The intensity of happiness, contentment, or pleasure. Scale: {MIN_EMOTION_VALUE} (no joy) to {MAX_EMOTION_VALUE} (extremely joyful)",
                                        "type": "number",
                                    },
                                },
                            },
                            "sadness": {
                                "description": f"The intensity of sorrow, grief, or disappointment. Scale: {MIN_EMOTION_VALUE} (no sadness) to {MAX_EMOTION_VALUE} (deeply sorrowful)",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"The intensity of sorrow, grief, or disappointment. Scale: {MIN_EMOTION_VALUE} (no sadness) to {MAX_EMOTION_VALUE} (deeply sorrowful)",
                                        "type": "number",
                                    },
                                },
                            },
                            "anger": {
                                "description": f"The intensity of frustration, irritation, or rage. Scale: {MIN_EMOTION_VALUE} (no anger) to {MAX_EMOTION_VALUE} (extremely angry)",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"The intensity of frustration, irritation, or rage. Scale: {MIN_EMOTION_VALUE} (no anger) to {MAX_EMOTION_VALUE} (extremely angry)",
                                        "type": "number",
                                    },
                                },
                            },
                            "fear": {
                                "description": f"The intensity of anxiety, dread, or apprehension. Scale: {MIN_EMOTION_VALUE} (no fear) to {MAX_EMOTION_VALUE} (extremely fearful)",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"The intensity of anxiety, dread, or apprehension. Scale: {MIN_EMOTION_VALUE} (no fear) to {MAX_EMOTION_VALUE} (extremely fearful)",
                                        "type": "number",
                                    },
                                },
                            },
                            "surprise": {
                                "description": f"The intensity of astonishment or being caught off guard. Scale: {MIN_EMOTION_VALUE} (no surprise) to {MAX_EMOTION_VALUE} (completely astonished)",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"The intensity of astonishment or being caught off guard. Scale: {MIN_EMOTION_VALUE} (no surprise) to {MAX_EMOTION_VALUE} (completely astonished)",
                                        "type": "number",
                                    },
                                },
                            },
                            "love": {
                                "description": f"The intensity of affection, attachment, or deep bonds. Scale: {MIN_EMOTION_VALUE} (no love) to {MAX_EMOTION_VALUE} (deeply loving)",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"The intensity of affection, attachment, or deep bonds. Scale: {MIN_EMOTION_VALUE} (no love) to {MAX_EMOTION_VALUE} (deeply loving)",
                                        "type": "number",
                                    },
                                },
                            },
                            "disgust": {
                                "description": f"The intensity of revulsion or strong aversion. Scale: {MIN_EMOTION_VALUE} (no disgust) to {MAX_EMOTION_VALUE} (extremely disgusted)",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"The intensity of revulsion or strong aversion. Scale: {MIN_EMOTION_VALUE} (no disgust) to {MAX_EMOTION_VALUE} (extremely disgusted)",
                                        "type": "number",
                                    },
                                },
                            },
                        },
                        "additionalProperties": False,
                    },
                    "reason": {
                        "description": "The reason for the emotional state change",
                        "type": "string",
                    },
                },
                "additionalProperties": False,
            },
        },
    }

def get_sentiment_status_schema_lite():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "sentiment_status_response",
            "schema": {
                "type": "object",
                "properties": {
                    "sentiments": {
                        "type": "object",
                        "properties": {
                            "positive": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"General positive feelings like affection, gratitude, admiration, or joy. Scale: {MIN_SENTIMENT_VALUE} (no positive sentiment) to {MAX_SENTIMENT_VALUE} (extreme positive sentiment)",
                                        "type": "number"
                                    }
                                }
                            },
                            "love": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Deep, multifaceted affection, care, and attachment to someone. Scale: {MIN_SENTIMENT_VALUE} (no love) to {MAX_SENTIMENT_VALUE} (deep love)",
                                        "type": "number"
                                    }
                                }
                            },
                            "hate": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Intense hostility, aversion, or strong dislike for someone. Scale: {MIN_SENTIMENT_VALUE} (no hate) to {MAX_SENTIMENT_VALUE} (deep hatred)",
                                        "type": "number"
                                    }
                                }
                            },
                            "trust": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Confidence in someone’s reliability or integrity. Scale: {MIN_SENTIMENT_VALUE} (no trust) to {MAX_SENTIMENT_VALUE} (deep trust)",
                                        "type": "number"
                                    }
                                }
                            },
                            "admiration": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Respect or appreciation for someone’s abilities or qualities. Scale: {MIN_SENTIMENT_VALUE} (no admiration) to {MAX_SENTIMENT_VALUE} (deep admiration)",
                                        "type": "number"
                                    }
                                }
                            },
                            "attachment": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Emotional closeness and bonding, including loyalty and devotion. Scale: {MIN_SENTIMENT_VALUE} (no attachment) to {MAX_SENTIMENT_VALUE} (deep attachment)",
                                        "type": "number"
                                    }
                                }
                            },
                            "empathy": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Understanding and sharing someone else’s emotions. Scale: {MIN_SENTIMENT_VALUE} (no empathy) to {MAX_SENTIMENT_VALUE} (deep empathy)",
                                        "type": "number"
                                    }
                                }
                            },
                            "curiosity": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Interest in learning more about someone. Scale: {MIN_SENTIMENT_VALUE} (no curiosity) to {MAX_SENTIMENT_VALUE} (intense curiosity)",
                                        "type": "number"
                                    }
                                }
                            },
                            "ambivalence": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Mixed or conflicting feelings toward someone. Scale: {MIN_SENTIMENT_VALUE} (no ambivalence) to {MAX_SENTIMENT_VALUE} (deep ambivalence)",
                                        "type": "number"
                                    }
                                }
                            },
                            "skepticism": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Doubt or mistrust about someone’s intentions. Scale: {MIN_SENTIMENT_VALUE} (no skepticism) to {MAX_SENTIMENT_VALUE} (deep skepticism)",
                                        "type": "number"
                                    }
                                }
                            },
                            "negativity": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"General negative feelings like anger, resentment, or disdain. Scale: {MIN_SENTIMENT_VALUE} (no negativity) to {MAX_SENTIMENT_VALUE} (deep negativity)",
                                        "type": "number"
                                    }
                                }
                            },
                            "fear": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Anxiety or apprehension about someone. Scale: {MIN_SENTIMENT_VALUE} (no fear) to {MAX_SENTIMENT_VALUE} (deep fear)",
                                        "type": "number"
                                    }
                                }
                            },
                            "sadness": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Emotional heaviness or grief. Scale: {MIN_SENTIMENT_VALUE} (no sadness) to {MAX_SENTIMENT_VALUE} (deep sadness)",
                                        "type": "number"
                                    }
                                }
                            },
                            "rejection": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"Feeling unwanted or cast aside by someone. Scale: {MIN_SENTIMENT_VALUE} (no rejection) to {MAX_SENTIMENT_VALUE} (deep rejection)",
                                        "type": "number"
                                    }
                                }
                            },
                            "protectiveness": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "description": f"A desire to shield someone from harm. Scale: {MIN_SENTIMENT_VALUE} (no protectiveness) to {MAX_SENTIMENT_VALUE} (deep protectiveness)",
                                        "type": "number"
                                    }
                                }
                            }
                        }
                    },
                    "reason": {
                        "description": "The reason for the sentiment state",
                        "type": "string"
                    }
                },
                "additionalProperties": False
            }
        }
    }

def get_emotion_delta_schema_lite():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "emotion_delta",
            "schema": {
                "type": "object",
                "properties": {
                    "deltas": {
                        "type": "object",
                        "additionalProperties": { "type": "number", "minimum": -15, "maximum": 15 }
                    },
                    "reason": { "type": "string" },
                    "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
                },
                "required": ["deltas"]
            }
        }
    }

def get_personality_delta_schema_lite():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "personality_delta",
            "schema": {
                "type": "object",
                "properties": {
                    "deltas": {
                        "type": "object",
                        "additionalProperties": { "type": "number", "minimum": -7, "maximum": 7 }
                    },
                    "reason": { "type": "string" },
                    "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
                },
                "required": ["deltas"]
            }
        }
    }