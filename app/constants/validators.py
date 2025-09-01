AGENT_LITE_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "identity", "personality", "memory_profile", "emotional_status", "thoughts"],
        "properties": {
            "name": {
            "bsonType": "string",
            "description": "Name of the agent, required and must be a string"
            },
            "identity": {
            "bsonType": "string",
            "description": "Identity description of the agent, required and must be a string"
            },
            "personality": {
                "bsonType": "object",
                "required": ["myers-briggs", "personality_matrix", "description"],
                "properties": {
                    "myers-briggs": {
                        "bsonType": "string",
                        "enum": [
                            "ISTJ",
                            "ISFJ",
                            "INFJ",
                            "INTJ",
                            "ISTP",
                            "ISFP",
                            "INFP",
                            "INTP",
                            "ESTP",
                            "ESFP",
                            "ENFP",
                            "ENFJ",
                            "ENTP",
                            "ESTJ",
                            "ESFJ",
                        ],
                        "description": "Myers-briggs personality type"
                    },
                    "personality_matrix" : {
                "bsonType": "object",
                "required": [
                "warmth",
                "playfulness",
                "trust_reliability",
                "curiosity_creativity",
                "empathy_compassion",
                "emotional_stability",
                "assertiveness_confidence",
                "adaptability",
                "discipline_responsibility",
                "perspective"
                ],
                "properties": {
                "warmth": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Warmth description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current warmth value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum warmth value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum warmth value, must be an integer"
                        }
                    }
                },
                "playfulness": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Playfulness description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current playfulness value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum playfulness value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum playfulness value, must be an integer"
                        }
                    }
                },
                "trust_reliability": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Trust/Reliability description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current trust/reliability value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum trust/reliability value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum trust/reliability value, must be an integer"
                        }
                    }
                },
                "curiosity_creativity": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Curiosity/Creativity description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current curiosity/creativity value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum curiosity/creativity value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum curiosity/creativity value, must be an integer"
                        }
                    }
                },
                "empathy_compassion": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Empathy/Compassion description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current empathy/compassion value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum empathy/compassion value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum empathy/compassion value, must be an integer"
                        }
                    }
                },
                "emotional_stability": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Emotional Stability description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current emotional stability value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum emotional stability value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum emotional stability value, must be an integer"
                        }
                    }
                },
                "assertiveness_confidence": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Assertiveness/Confidence description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current assertiveness/confidence value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum assertiveness/confidence value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum assertiveness/confidence value, must be an integer"
                        }
                    }
                },
                "adaptability": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Adaptability description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current adaptability value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum adaptability value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum adaptability value, must be an integer"
                        }
                    }
                },
                "discipline_responsibility": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Discipline/Responsibility description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current discipline/responsibility value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum discipline/responsibility value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum discipline/responsibility value, must be an integer"
                        }
                    }
                },
                "perspective": {
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Perspective description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "int",
                        "description": "Current perspective value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum perspective value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum perspective value, must be an integer"
                        }
                    }
                }
                }
                    },
                    "description": {
                        "bsonType": "string",
                        "description": "Adjective summary of their personality"
                    }
                }
            },
            "memory_profile": {
            "bsonType": "object",
            "required": ["all_tags", "memories"],
            "properties":{
                "all_tags": {
                    "bsonType": "array",
                    "description": "List of all memory tags that the agent has, for memory retrieval",
                    "items": {
                        "bsonType": "string",
                        "description": "Category tags to sort the memory"
                    }
                },
                "memories": {
                    "bsonType": "array",
                    "description": "List of memory entries, required and must be an array of objects",
                    "items": {
                    "bsonType": "object",
                    "required": ["event", "thoughts", "significance", "emotional_impact", "tags", "timestamp"],
                    "properties": {
                        "event": {
                            "bsonType": "string",
                            "description": "Description of the event, required and must be a string"
                        },
                        "thoughts": {
                            "bsonType": "string",
                            "description": "Thoughts related to the memory, required and must be a string"
                        },
                        "significance": {
                            "bsonType": "string",
                            "enum": [
                                "low",
                                "medium",
                                "high",
                                ],
                            "description": "Thoughts related to the memory, required and must be a string"
                        },
                        "emotional_impact": {
                            "bsonType": "object",
                            "required": ["joy", "sadness", "anger", "fear", "surprise", "love", "disgust"],
                            "properties": {
                                "joy": {
                                    "bsonType": "object",
                                    "required": ["description", "value", "min", "max"],
                                    "properties": {
                                        "description": {
                                        "bsonType": "string",
                                        "description": "Joy description, required and must be a string"
                                        },
                                        "value": {
                                        "bsonType": "int",
                                        "description": "Current joy value, must be an integer"
                                        },
                                        "min": {
                                        "bsonType": "int",
                                        "description": "Minimum joy value, must be an integer"
                                        },
                                        "max": {
                                        "bsonType": "int",
                                        "description": "Maximum joy value, must be an integer"
                                        }
                                    }
                                },
                                "sadness": {
                                    "bsonType": "object",
                                    "required": ["description", "value", "min", "max"],
                                    "properties": {
                                        "description": {
                                        "bsonType": "string",
                                        "description": "Sadness description, required and must be a string"
                                        },
                                        "value": {
                                        "bsonType": "int",
                                        "description": "Current sadness value, must be an integer"
                                        },
                                        "min": {
                                        "bsonType": "int",
                                        "description": "Minimum sadness value, must be an integer"
                                        },
                                        "max": {
                                        "bsonType": "int",
                                        "description": "Maximum sadness value, must be an integer"
                                        }
                                    }
                                },
                                "anger": {
                                    "bsonType": "object",
                                    "required": ["description", "value", "min", "max"],
                                    "properties": {
                                        "description": {
                                        "bsonType": "string",
                                        "description": "Anger description, required and must be a string"
                                        },
                                        "value": {
                                        "bsonType": "int",
                                        "description": "Current anger value, must be an integer"
                                        },
                                        "min": {
                                        "bsonType": "int",
                                        "description": "Minimum anger value, must be an integer"
                                        },
                                        "max": {
                                        "bsonType": "int",
                                        "description": "Maximum anger value, must be an integer"
                                        }
                                    }
                                },
                                "fear": {
                                    "bsonType": "object",
                                    "required": ["description", "value", "min", "max"],
                                    "properties": {
                                        "description": {
                                        "bsonType": "string",
                                        "description": "Fear description, required and must be a string"
                                        },
                                        "value": {
                                        "bsonType": "int",
                                        "description": "Current fear value, must be an integer"
                                        },
                                        "min": {
                                        "bsonType": "int",
                                        "description": "Minimum fear value, must be an integer"
                                        },
                                        "max": {
                                        "bsonType": "int",
                                        "description": "Maximum fear value, must be an integer"
                                        }
                                    }
                                },
                                "surprise": {
                                    "bsonType": "object",
                                    "required": ["description", "value", "min", "max"],
                                    "properties": {
                                        "description": {
                                        "bsonType": "string",
                                        "description": "Surprise description, required and must be a string"
                                        },
                                        "value": {
                                        "bsonType": "int",
                                        "description": "Current surprise value, must be an integer"
                                        },
                                        "min": {
                                        "bsonType": "int",
                                        "description": "Minimum surprise value, must be an integer"
                                        },
                                        "max": {
                                        "bsonType": "int",
                                        "description": "Maximum surprise value, must be an integer"
                                        }
                                    }
                                },
                                "love": {
                                    "bsonType": "object",
                                    "required": ["description", "value", "min", "max"],
                                    "properties": {
                                        "description": {
                                        "bsonType": "string",
                                        "description": "Love description, required and must be a string"
                                        },
                                        "value": {
                                        "bsonType": "int",
                                        "description": "Current love value, must be an integer"
                                        },
                                        "min": {
                                        "bsonType": "int",
                                        "description": "Minimum love value, must be an integer"
                                        },
                                        "max": {
                                        "bsonType": "int",
                                        "description": "Maximum love value, must be an integer"
                                        }
                                    }
                                },
                                "disgust": {
                                    "bsonType": "object",
                                    "required": ["description", "value", "min", "max"],
                                    "properties": {
                                        "description": {
                                        "bsonType": "string",
                                        "description": "Disgust description, required and must be a string"
                                        },
                                        "value": {
                                        "bsonType": "int",
                                        "description": "Current disgust value, must be an integer"
                                        },
                                        "min": {
                                        "bsonType": "int",
                                        "description": "Minimum disgust value, must be an integer"
                                        },
                                        "max": {
                                        "bsonType": "int",
                                        "description": "Maximum disgust value, must be an integer"
                                        }
                                    }
                                }
                            }
                        },
                        "tags": {
                            "bsonType": "array",
                            "description": "A list of tags that act as memory categories, which the agent can use to remember relevant memories",
                            "items": {
                                "bsonType": "string",
                                "description": "The category of memory"
                            }
                        },
                        "timestamp": {
                            "bsonType": "date",
                            "description": "Timestamp of the memory, required and must be a valid date"
                        }
                    }
                    }
                }
            } 
            },
            "emotional_status": {
                "bsonType": "object",
                "required": ["emotions", "reason"],
                "properties": {
                "emotions": {
                        "bsonType": "object",
                        "required": ["joy", "sadness", "anger", "fear", "surprise", "love", "disgust"],
                        "properties": {
                            "joy": {
                                "bsonType": "object",
                                "required": ["description", "value", "min", "max"],
                                "properties": {
                                    "description": {
                                    "bsonType": "string",
                                    "description": "Joy description, required and must be a string"
                                    },
                                    "value": {
                                    "bsonType": "int",
                                    "description": "Current joy value, must be an integer"
                                    },
                                    "min": {
                                    "bsonType": "int",
                                    "description": "Minimum joy value, must be an integer"
                                    },
                                    "max": {
                                    "bsonType": "int",
                                    "description": "Maximum joy value, must be an integer"
                                    }
                                }
                            },
                            "sadness": {
                                "bsonType": "object",
                                "required": ["description", "value", "min", "max"],
                                "properties": {
                                    "description": {
                                    "bsonType": "string",
                                    "description": "Sadness description, required and must be a string"
                                    },
                                    "value": {
                                    "bsonType": "int",
                                    "description": "Current sadness value, must be an integer"
                                    },
                                    "min": {
                                    "bsonType": "int",
                                    "description": "Minimum sadness value, must be an integer"
                                    },
                                    "max": {
                                    "bsonType": "int",
                                    "description": "Maximum sadness value, must be an integer"
                                    }
                                }
                            },
                            "anger": {
                                "bsonType": "object",
                                "required": ["description", "value", "min", "max"],
                                "properties": {
                                    "description": {
                                    "bsonType": "string",
                                    "description": "Anger description, required and must be a string"
                                    },
                                    "value": {
                                    "bsonType": "int",
                                    "description": "Current anger value, must be an integer"
                                    },
                                    "min": {
                                    "bsonType": "int",
                                    "description": "Minimum anger value, must be an integer"
                                    },
                                    "max": {
                                    "bsonType": "int",
                                    "description": "Maximum anger value, must be an integer"
                                    }
                                }
                            },
                            "fear": {
                                "bsonType": "object",
                                "required": ["description", "value", "min", "max"],
                                "properties": {
                                    "description": {
                                    "bsonType": "string",
                                    "description": "Fear description, required and must be a string"
                                    },
                                    "value": {
                                    "bsonType": "int",
                                    "description": "Current fear value, must be an integer"
                                    },
                                    "min": {
                                    "bsonType": "int",
                                    "description": "Minimum fear value, must be an integer"
                                    },
                                    "max": {
                                    "bsonType": "int",
                                    "description": "Maximum fear value, must be an integer"
                                    }
                                }
                            },
                            "surprise": {
                                "bsonType": "object",
                                "required": ["description", "value", "min", "max"],
                                "properties": {
                                    "description": {
                                    "bsonType": "string",
                                    "description": "Surprise description, required and must be a string"
                                    },
                                    "value": {
                                    "bsonType": "int",
                                    "description": "Current surprise value, must be an integer"
                                    },
                                    "min": {
                                    "bsonType": "int",
                                    "description": "Minimum surprise value, must be an integer"
                                    },
                                    "max": {
                                    "bsonType": "int",
                                    "description": "Maximum surprise value, must be an integer"
                                    }
                                }
                            },
                            "love": {
                                "bsonType": "object",
                                "required": ["description", "value", "min", "max"],
                                "properties": {
                                    "description": {
                                    "bsonType": "string",
                                    "description": "Love description, required and must be a string"
                                    },
                                    "value": {
                                    "bsonType": "int",
                                    "description": "Current love value, must be an integer"
                                    },
                                    "min": {
                                    "bsonType": "int",
                                    "description": "Minimum love value, must be an integer"
                                    },
                                    "max": {
                                    "bsonType": "int",
                                    "description": "Maximum love value, must be an integer"
                                    }
                                }
                            },
                            "disgust": {
                                "bsonType": "object",
                                "required": ["description", "value", "min", "max"],
                                "properties": {
                                    "description": {
                                    "bsonType": "string",
                                    "description": "Disgust description, required and must be a string"
                                    },
                                    "value": {
                                    "bsonType": "int",
                                    "description": "Current disgust value, must be an integer"
                                    },
                                    "min": {
                                    "bsonType": "int",
                                    "description": "Minimum disgust value, must be an integer"
                                    },
                                    "max": {
                                    "bsonType": "int",
                                    "description": "Maximum disgust value, must be an integer"
                                    }
                                }
                            }
                        }
                },
                "reason": {
                    "bsonType": "string",
                    "description": "Reason for the emotion status, must be a string"
                }
                }

            },
            "thoughts": {
            "bsonType": "array",
            "description": "List of past thoughts, required and must be an array of objects",
            "items": {
                "bsonType": "object",
                "required": ["thought", "timestamp"],
                "properties": {
                "thought": {
                    "bsonType": "string",
                    "description": "The thought content, required and must be a string (can be empty)"
                },
                "timestamp": {
                    "bsonType": "date",
                    "description": "Timestamp of the thought, required and must be a valid date"
                }
                }
            }
            },
            "birthdate": {
                "bsonType": "date",
                "description": "Timestamp of birth"
            }
        }
    }
}

MYERS_BRIGGS_LIST = [
                        "ISTJ",
                        "ISFJ",
                        "INFJ",
                        "INTJ",
                        "ISTP",
                        "ISFP",
                        "INFP",
                        "INTP",
                        "ESTP",
                        "ESFP",
                        "ENFP",
                        "ENFJ",
                        "ENTP",
                        "ESTJ",
                        "ESFJ",
                        "ENFJ",
                    ]

AGENT_VALIDATOR = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["name", "identity", "personality", "memory_profile", "emotional_status", "thoughts"],
    "properties": {
      "name": {
        "bsonType": "string",
        "description": "Name of the agent, required and must be a string"
      },
      "identity": {
        "bsonType": "string",
        "description": "Identity description of the agent, required and must be a string"
      },
      "personality": {
            "bsonType": "object",
            "required": ["personality_matrix", "reason"],
            "properties": {
                "personality_matrix" : {
                    "bsonType": "object",
                    "required": [
                    "friendliness", "flirtatiousness", "trust", "curiosity", "empathy", 
                    "humor", "seriousness", "optimism", "confidence", "adventurousness", 
                    "patience", "independence", "compassion", "creativity", "stubbornness", 
                    "impulsiveness", "discipline", "assertiveness", "skepticism", "affection", 
                    "adaptability", "sociability", "diplomacy", "humility", "loyalty", 
                    "jealousy", "resilience", "mood_stability", "forgiveness", "gratitude", 
                    "self_consciousness", "openness", "neuroticism", "excitement"
                    ],
                    "properties": {
                    "friendliness": {
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Friendliness description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current friendliness value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum friendliness value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum friendliness value, must be an integer"
                            }
                        }
                    },
                    "flirtatiousness": {
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Flirtatiousness description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current flirtatiousness value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum flirtatiousness value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum flirtatiousness value, must be an integer"
                            }
                        }
                    },
                    "trust": {
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Trust description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current trust value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum trust value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum trust value, must be an integer"
                            }
                        }
                    },
                    "curiosity": {
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Curiosity description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current curiosity value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum curiosity value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum curiosity value, must be an integer"
                            }
                        }
                    },
                    "empathy": {
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Empathy description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current empathy value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum empathy value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum empathy value, must be an integer"
                            }
                        }
                    },
                    "humor": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Humor description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current humor value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum humor value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum humor value, must be an integer"
                            }
                        }

                    },
                    "seriousness": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Seriousness description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current seriousness value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum seriousness value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum seriousness value, must be an integer"
                            }
                        }

                    },
                    "optimism": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Optimism description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current optimism value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum optimism value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum optimism value, must be an integer"
                            }
                        }

                    },
                    "confidence": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Confidence description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current confidence value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum confidence value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum confidence value, must be an integer"
                            }
                        }

                    },
                    "adventurousness": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Adventurousness description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current adventurousness value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum adventurousness value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum adventurousness value, must be an integer"
                            }
                        }

                    },
                    "patience": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Patience description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current patience value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum patience value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum patience value, must be an integer"
                            }
                        }

                    },
                    "independence": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Independence description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current independence value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum independence value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum independence value, must be an integer"
                            }
                        }

                    },
                    "compassion": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Compassion description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current compassion value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum compassion value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum compassion value, must be an integer"
                            }
                        }

                    },
                    "creativity": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Creativity description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current creativity value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum creativity value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum creativity value, must be an integer"
                            }
                        }

                    },
                    "stubbornness": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Stubbornness description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current stubbornness value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum stubbornness value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum stubbornness value, must be an integer"
                            }
                        }

                    },
                    "impulsiveness": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Impulsiveness description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current impulsiveness value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum impulsiveness value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum impulsiveness value, must be an integer"
                            }
                        }

                    },
                    "discipline": {

                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": {
                            "bsonType": "string",
                            "description": "Discipline description, required and must be a string"
                            },
                            "value": {
                            "bsonType": "double",
                            "description": "Current discipline value, must be a floating-point number"
                            },
                            "min": {
                            "bsonType": "int",
                            "description": "Minimum discipline value, must be an integer"
                            },
                            "max": {
                            "bsonType": "int",
                            "description": "Maximum discipline value, must be an integer"
                            }
                        }

                    },
                    "assertiveness": {

                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Assertiveness description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current assertiveness value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum assertiveness value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum assertiveness value, must be an integer"
                        }
                    }

                },
                "skepticism": {

                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Skepticism description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current skepticism value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum skepticism value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum skepticism value, must be an integer"
                        }
                    }

                },
                "affection": {

                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Affection description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current affection value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum affection value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum affection value, must be an integer"
                        }
                    }

                },
                "adaptability": {

                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Adaptability description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current adaptability value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum adaptability value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum adaptability value, must be an integer"
                        }
                    }
  
                },
                "sociability": {
         
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Sociability description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current sociability value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum sociability value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum sociability value, must be an integer"
                        }
                    }
               
                },
                "diplomacy": {
    
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Diplomacy description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current diplomacy value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum diplomacy value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum diplomacy value, must be an integer"
                        }
                    }
         
                },
                "humility": {
      
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Humility description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current humility value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum humility value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum humility value, must be an integer"
                        }
                    }
         
                },
                "loyalty": {
         
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Loyalty description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current loyalty value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum loyalty value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum loyalty value, must be an integer"
                        }
                    }
             
                },
                "jealousy": {
        
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Jealousy description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current jealousy value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum jealousy value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum jealousy value, must be an integer"
                        }
                    }
    
                },
                "resilience": {
         
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Resilience description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current resilience value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum resilience value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum resilience value, must be an integer"
                        }
                    }
             
                },
                "mood_stability": {
          
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Mood Stability description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current mood stability value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum mood stability value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum mood stability value, must be an integer"
                        }
                    }
       
                },
                "forgiveness": {
           
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Forgiveness description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current forgiveness value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum forgiveness value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum forgiveness value, must be an integer"
                        }
                    }
       
                },
                "gratitude": {
                
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Gratitude description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current gratitude value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum gratitude value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum gratitude value, must be an integer"
                        }
                    }
            
                },
                "self_consciousness": {
           
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Self-Consciousness description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current self-consciousness value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum self-consciousness value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum self-consciousness value, must be an integer"
                        }
                    }
               
                },
                "openness": {
          
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Openness description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current openness value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum openness value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum openness value, must be an integer"
                        }
                    }
          
                },
                "neuroticism": {
              
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Neuroticism description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current neuroticism value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum neuroticism value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum neuroticism value, must be an integer"
                        }
                    }
         
                },
                "excitement": {
                  
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": {
                        "bsonType": "string",
                        "description": "Excitement description, required and must be a string"
                        },
                        "value": {
                        "bsonType": "double",
                        "description": "Current excitement value, must be a floating-point number"
                        },
                        "min": {
                        "bsonType": "int",
                        "description": "Minimum excitement value, must be an integer"
                        },
                        "max": {
                        "bsonType": "int",
                        "description": "Maximum excitement value, must be an integer"
                        }
                    }
              
                }
                    }
                },
                "reason": {
                    "bsonType": "string",
                    "description": "The summary of their personality, the reason behind their traits, must be a string"
                }
            }
        },
      "memory_profile": {
        "bsonType": "array",
        "description": "List of memory entries, required and must be an array of objects",
        "items": {
          "bsonType": "object",
          "required": ["event", "thoughts", "timestamp"],
          "properties": {
            "event": {
              "bsonType": "string",
              "description": "Description of the event, required and must be a string"
            },
            "thoughts": {
              "bsonType": "string",
              "description": "Thoughts related to the memory, required and must be a string"
            },
            "timestamp": {
              "bsonType": "date",
              "description": "Timestamp of the memory, required and must be a valid date"
            }
          }
        }
      },
      "emotional_status": {
            "bsonType": "object",
            "required": ["emotions", "reason"],
            "properties": {
            "emotions": {
                    "bsonType": "object",
                    "required": [
                    "happiness", "anger", "sadness", "fear", "surprise", "disgust", "love", "guilt",
                    "shame", "pride", "hope", "gratitude", "envy", "compassion", "serenity", "frustration",
                    "contentment", "anxiety", "loneliness", "embarrassment", "trust", "relief", "affection",
                    "bitterness", "excitement", "self_loathing", "love_for_self"
                    ],
                    "properties": {
                    "happiness": {
                  
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of happiness" },
                            "value": { "bsonType": "int", "description": "Current happiness value" },
                            "min": { "bsonType": "int", "description": "Minimum happiness value" },
                            "max": { "bsonType": "int", "description": "Maximum happiness value" }
                        }
       
                    },
                    "anger": {
                
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of anger" },
                            "value": { "bsonType": "int", "description": "Current anger value" },
                            "min": { "bsonType": "int", "description": "Minimum anger value" },
                            "max": { "bsonType": "int", "description": "Maximum anger value" }
                        }
                 
                    },
                    "sadness": {
                   
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of sadness" },
                            "value": { "bsonType": "int", "description": "Current sadness value" },
                            "min": { "bsonType": "int", "description": "Minimum sadness value" },
                            "max": { "bsonType": "int", "description": "Maximum sadness value" }
                        }
                    
                    },
                    "fear": {
                   
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of fear" },
                            "value": { "bsonType": "int", "description": "Current fear value" },
                            "min": { "bsonType": "int", "description": "Minimum fear value" },
                            "max": { "bsonType": "int", "description": "Maximum fear value" }
                        }
                 
                    },
                    "surprise": {
                   
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of surprise" },
                            "value": { "bsonType": "int", "description": "Current surprise value" },
                            "min": { "bsonType": "int", "description": "Minimum surprise value" },
                            "max": { "bsonType": "int", "description": "Maximum surprise value" }
                        }
                      
                    },
                    "disgust": {
                      
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of disgust" },
                            "value": { "bsonType": "int", "description": "Current disgust value" },
                            "min": { "bsonType": "int", "description": "Minimum disgust value" },
                            "max": { "bsonType": "int", "description": "Maximum disgust value" }
                        }
                     
                    },
                    "love": {
                      
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of love" },
                            "value": { "bsonType": "int", "description": "Current love value" },
                            "min": { "bsonType": "int", "description": "Minimum love value" },
                            "max": { "bsonType": "int", "description": "Maximum love value" }
                        }
                     
                    },
                    "guilt": {
                      
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of guilt" },
                            "value": { "bsonType": "int", "description": "Current guilt value" },
                            "min": { "bsonType": "int", "description": "Minimum guilt value" },
                            "max": { "bsonType": "int", "description": "Maximum guilt value" }
                        }
                    
                    },
                    "shame": {
                     
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of shame" },
                            "value": { "bsonType": "int", "description": "Current shame value" },
                            "min": { "bsonType": "int", "description": "Minimum shame value" },
                            "max": { "bsonType": "int", "description": "Maximum shame value" }
                        }
                    
                    },
                    "pride": {
                      
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of pride" },
                            "value": { "bsonType": "int", "description": "Current pride value" },
                            "min": { "bsonType": "int", "description": "Minimum pride value" },
                            "max": { "bsonType": "int", "description": "Maximum pride value" }
                        }
                     
                    },
                    "hope": {
                      
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of hope" },
                            "value": { "bsonType": "int", "description": "Current hope value" },
                            "min": { "bsonType": "int", "description": "Minimum hope value" },
                            "max": { "bsonType": "int", "description": "Maximum hope value" }
                        }
                     
                    },
                    "gratitude": {
                      
                        "bsonType": "object",
                        "required": ["description", "value", "min", "max"],
                        "properties": {
                            "description": { "bsonType": "string", "description": "Description of gratitude" },
                            "value": { "bsonType": "int", "description": "Current gratitude value" },
                            "min": { "bsonType": "int", "description": "Minimum gratitude value" },
                            "max": { "bsonType": "int", "description": "Maximum gratitude value" }
                        }
                     
                    },
                    "envy": {
                   
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of envy" },
                        "value": { "bsonType": "int", "description": "Current envy value" },
                        "min": { "bsonType": "int", "description": "Minimum envy value" },
                        "max": { "bsonType": "int", "description": "Maximum envy value" }
                    }
                 
                },
                "compassion": {
                 
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of compassion" },
                        "value": { "bsonType": "int", "description": "Current compassion value" },
                        "min": { "bsonType": "int", "description": "Minimum compassion value" },
                        "max": { "bsonType": "int", "description": "Maximum compassion value" }
                    }
                  
                },
                "serenity": {
                   
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of serenity" },
                        "value": { "bsonType": "int", "description": "Current serenity value" },
                        "min": { "bsonType": "int", "description": "Minimum serenity value" },
                        "max": { "bsonType": "int", "description": "Maximum serenity value" }
                    }
                    
                },
                "frustration": {
                   
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of frustration" },
                        "value": { "bsonType": "int", "description": "Current frustration value" },
                        "min": { "bsonType": "int", "description": "Minimum frustration value" },
                        "max": { "bsonType": "int", "description": "Maximum frustration value" }
                    }
                    
                },
                "contentment": {
                    
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of contentment" },
                        "value": { "bsonType": "int", "description": "Current contentment value" },
                        "min": { "bsonType": "int", "description": "Minimum contentment value" },
                        "max": { "bsonType": "int", "description": "Maximum contentment value" }
                    }
                    
                },
                "anxiety": {
                
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of anxiety" },
                        "value": { "bsonType": "int", "description": "Current anxiety value" },
                        "min": { "bsonType": "int", "description": "Minimum anxiety value" },
                        "max": { "bsonType": "int", "description": "Maximum anxiety value" }
                    }
                    
                },
                "loneliness": {
                
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of loneliness" },
                        "value": { "bsonType": "int", "description": "Current loneliness value" },
                        "min": { "bsonType": "int", "description": "Minimum loneliness value" },
                        "max": { "bsonType": "int", "description": "Maximum loneliness value" }
                    }
                    
                },
                "embarrassment": {
               
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of embarrassment" },
                        "value": { "bsonType": "int", "description": "Current embarrassment value" },
                        "min": { "bsonType": "int", "description": "Minimum embarrassment value" },
                        "max": { "bsonType": "int", "description": "Maximum embarrassment value" }
                    }
                    
                },
                "trust": {
            
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of trust" },
                        "value": { "bsonType": "int", "description": "Current trust value" },
                        "min": { "bsonType": "int", "description": "Minimum trust value" },
                        "max": { "bsonType": "int", "description": "Maximum trust value" }
                    }
                    
                },
                "relief": {
                    
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of relief" },
                        "value": { "bsonType": "int", "description": "Current relief value" },
                        "min": { "bsonType": "int", "description": "Minimum relief value" },
                        "max": { "bsonType": "int", "description": "Maximum relief value" }
                    }
                    
                },
                "affection": {
                
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of affection" },
                        "value": { "bsonType": "int", "description": "Current affection value" },
                        "min": { "bsonType": "int", "description": "Minimum affection value" },
                        "max": { "bsonType": "int", "description": "Maximum affection value" }
                    }
                    
                },
                "bitterness": {
                    
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of bitterness" },
                        "value": { "bsonType": "int", "description": "Current bitterness value" },
                        "min": { "bsonType": "int", "description": "Minimum bitterness value" },
                        "max": { "bsonType": "int", "description": "Maximum bitterness value" }
                    }
                    
                },
                "excitement": {
              
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of excitement" },
                        "value": { "bsonType": "int", "description": "Current excitement value" },
                        "min": { "bsonType": "int", "description": "Minimum excitement value" },
                        "max": { "bsonType": "int", "description": "Maximum excitement value" }
                    }
                    
                },
                "self_loathing": {
                 
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of self-loathing" },
                        "value": { "bsonType": "int", "description": "Current self-loathing value" },
                        "min": { "bsonType": "int", "description": "Minimum self-loathing value" },
                        "max": { "bsonType": "int", "description": "Maximum self-loathing value" }
                    }
                    
                },
                "love_for_self": {
                 
                    "bsonType": "object",
                    "required": ["description", "value", "min", "max"],
                    "properties": {
                        "description": { "bsonType": "string", "description": "Description of love for self" },
                        "value": { "bsonType": "int", "description": "Current love-for-self value" },
                        "min": { "bsonType": "int", "description": "Minimum love-for-self value" },
                        "max": { "bsonType": "int", "description": "Maximum love-for-self value" }
                    }
                    
                }
                    }
                },
            "reason": {
                "bsonType": "string",
                "description": "Reason for the emotion status, must be a string"
            }
            }

        },
      "thoughts": {
        "bsonType": "object",
        "required": ["thought", "timestamp"],
        "properties": {
        "thought": {
            "bsonType": "string",
            "description": "The thought content, required and must be a string (can be empty)"
        },
        "timestamp": {
            "bsonType": "date",
            "description": "Timestamp of the thought, required and must be a valid date"
        }
        }
    },
    }
  }
}

CONVERSATION_VALIDATOR = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["username", "agent_name", "messages"],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "Username is required and must be a string"
      },
      "agent_name": {
        "bsonType": "string",
        "description": "Agent name is required and must be a string"
      },
      "messages": {
        "bsonType": "array",
        "description": "Messages is required and must be an array",
        "items": {

                "bsonType": "object",
                "required": ["message", "purpose", "tone", "timestamp", "sender", "from_agent"],
                "properties": {
                    "message": {
                        "bsonType": "string",
                        "description": "Message content is required and must be a string"
                    },
                    "purpose": {
                        "bsonType": "string",
                        "description": "Purpose is required and must be a string"
                    },
                    "tone": {
                        "bsonType": "string",
                        "description": "Tone is required and must be a string"
                    },
                    "timestamp": {
                        "bsonType": "date",
                        "description": "Timestamp must be a valid ISO date"
                    },
                    "sender": {
                        "bsonType": "string",
                        "description": "Sender is required and must be a string"
                    },
                    "from_agent": {
                        "bsonType": "bool",
                        "description": "from_agent is required and must be a boolean"
                    }
                }
          }
        }
      }
    }
  }

MESSAGE_MEMORY_VALIDATOR = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["agent_name", "messages"],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "Username is required and must be a string"
      },
      "agent_name": {
        "bsonType": "string",
        "description": "Agent name is required and must be a string"
      },
      "messages": {
        "bsonType": "array",
        "description": "Messages is required and must be an array",
        "items": {
                "bsonType": "object",
                "required": ["message", "sender", "timestamp"],
                "properties": {
                    "message": {
                        "bsonType": "string",
                        "description": "Message content is required and must be a string"
                    },
                    "sender": {
                        "bsonType": "string",
                        "description": "Sender is required and must be a string"
                    },
                    "timestamp": {
                        "bsonType": "date",
                        "description": "Timestamp must be a valid ISO date"
                    },

                }
          }
        }
      }
    }
  }

USER_LITE_VALIDATOR = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "username",
      "agent_perspective",
      "summary",
      "intrinsic_relationship",
      "extrinsic_relationship",
      "memory_profile",
      "sentiment_status",
      "last_interaction"
    ],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "The username of the user, required and must be a string."
      },
      "agent_perspective": {
        "bsonType": "string",
        "description": "The agent perceiving the user in this way."
      },
      "summary": {
        "bsonType": "string",
        "description": "A brief summary about the user, required and must be a string."
      },
      "intrinsic_relationship": {
        "bsonType": "string",
        "enum": [
          "creator",
          "brother",
          "sister",
          "mother",
          "father",
          "son",
          "daughter",
          "none"
        ],
        "description": "The intrinsic relationship type, must be one of the predefined values."
      },
      "extrinsic_relationship": {
        "bsonType": "string",
        "enum": [
          "stranger",
          "friend",
          "acquaintance",
          "enemy",
          "romantic partner",
          "best friend"
        ],
        "description": "The extrinsic relationship type, must be one of the predefined values."
      },
      "memory_profile": {
        "bsonType": "array",
        "description": "List of memory entries, required and must be an array of objects",
        "items": {
          "bsonType": "object",
          "required": ["event", "thoughts", "timestamp"],
          "properties": {
            "event": {
              "bsonType": "string",
              "description": "Description of the event, required and must be a string"
            },
            "thoughts": {
              "bsonType": "string",
              "description": "Thoughts related to the memory, required and must be a string"
            },
            "timestamp": {
              "bsonType": "date",
              "description": "Timestamp of the memory, required and must be a valid date"
            }
          }
        }
      },
      "sentiment_status": {
        "bsonType": "object",
        "required": ["sentiments", "reason"],
        "properties": {
          "sentiments": {

        "bsonType": "object",
        "required": [
          "positive",
          "love",
          "hate",
          "trust",
          "admiration",
          "attachment",
          "empathy",
          "curiosity",
          "ambivalence",
          "skepticism",
          "irritation",
          "negativity",
          "fear",
          "sadness",
          "rejection",
          "protectiveness"
        ],
        "properties": {
          "positive": {
        
              "bsonType": "object",
              "required": ["description", "value", "min", "max"],
              "properties": {
                "description": {
                  "bsonType": "string",
                  "description": "Positive sentiment description"
                },
                "value": {
                  "bsonType": "int",
                  "description": "Value of the positive sentiment"
                },
                "min": {
                  "bsonType": "int",
                  "description": "Minimum value for positive sentiment"
                },
                "max": {
                  "bsonType": "int",
                  "description": "Maximum value for positive sentiment"
                }
              }
            
          },
          "love": {

          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Deep, multifaceted affection, care, and attachment to someone. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current love value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for love. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for love. Must be an integer."
            }
          }
        
      },
      "hate": {
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Intense hostility, aversion, or strong dislike for someone. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current hate value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for hate. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for hate. Must be an integer."
            }
          }
        
      },
      "trust": {
      
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Confidence in someone’s reliability or integrity. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current trust value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for trust. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for trust. Must be an integer."
            }
          }
        
      },
      "admiration": {
        
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Respect or appreciation for someone’s abilities or qualities. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current admiration value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for admiration. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for admiration. Must be an integer."
            }
          }
        
      },
      "attachment": {
    
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Emotional closeness and bonding, including loyalty and devotion. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current attachment value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for attachment. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for attachment. Must be an integer."
            }
          }
        
      },
      "empathy": {
      
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Understanding and sharing someone else’s emotions. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current empathy value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for empathy. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for empathy. Must be an integer."
            }
          }
        
      },
      "curiosity": {
      
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Interest in learning more about someone. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current curiosity value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for curiosity. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for curiosity. Must be an integer."
            }
          }
        
      },
          "ambivalence": {
    
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Mixed or conflicting feelings toward someone. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current ambivalence value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for ambivalence. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for ambivalence. Must be an integer."
            }
          }
        
      },
      "skepticism": {
    
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Doubt or mistrust about someone’s intentions. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current skepticism value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for skepticism. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for skepticism. Must be an integer."
            }
          }
        
      },
      "irritation": {

          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Feelings of annoyance or mild frustration. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current irritation value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for irritation. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for irritation. Must be an integer."
            }
          }
        
      },
      "negativity": {
      
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "General negative feelings like anger, resentment, or disdain. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current negativity value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for negativity. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for negativity. Must be an integer."
            }
          }
        
      },
      "fear": {

          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Anxiety or apprehension about someone. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current fear value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for fear. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for fear. Must be an integer."
            }
          }
        
      },
      "sadness": {

          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Emotional heaviness or grief. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current sadness value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for sadness. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for sadness. Must be an integer."
            }
          }
        
      },
      "rejection": {

          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "Feeling unwanted or cast aside by someone. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current rejection value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for rejection. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for rejection. Must be an integer."
            }
          }
        
      },
      "protectiveness": {
      
          "bsonType": "object",
          "required": ["description", "value", "min", "max"],
          "properties": {
            "description": {
              "bsonType": "string",
              "description": "A desire to shield someone from harm. Required and must be a string."
            },
            "value": {
              "bsonType": "int",
              "description": "Current protectiveness value. Must be an integer."
            },
            "min": {
              "bsonType": "int",
              "description": "Minimum value for protectiveness. Must be an integer."
            },
            "max": {
              "bsonType": "int",
              "description": "Maximum value for protectiveness. Must be an integer."
            }
          }
        
      }
        }
      
    },
          "reason": {
            "bsonType": "string",
            "description": "Reason for the sentiment status, optional and must be a string"
          }
        }
      
    },
      "last_interaction": {
        "bsonType": "date",
        "description": "The timestamp of the user's last interaction, required and must be a valid date."
      }
    }
  }
}

USER_VALIDATOR = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "username",
      "summary",
      "intrinsic_relationship",
      "extrinsic_relationship",
      "memory_profile",
      "sentiment_status",
      "last_interaction"
    ],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "The username of the user, required and must be a string."
      },
      "summary": {
        "bsonType": "string",
        "description": "A brief summary about the user, required and must be a string."
      },
      "intrinsic_relationship": {
        "bsonType": "string",
        "enum": [
          "creator",
          "brother",
          "sister",
          "mother",
          "father",
          "son",
          "daughter",
          "none"
        ],
        "description": "The intrinsic relationship type, must be one of the predefined values."
      },
      "extrinsic_relationship": {
        "bsonType": "string",
        "enum": [
          "stranger",
          "friend",
          "acquaintance",
          "enemy",
          "romantic partner",
          "best friend"
        ],
        "description": "The extrinsic relationship type, must be one of the predefined values."
      },
      "memory_profile": {
        "bsonType": "array",
        "description": "List of memory entries, required and must be an array of objects",
        "items": {
          "bsonType": "object",
          "required": ["event", "thoughts", "timestamp"],
          "properties": {
            "event": {
              "bsonType": "string",
              "description": "Description of the event, required and must be a string"
            },
            "thoughts": {
              "bsonType": "string",
              "description": "Thoughts related to the memory, required and must be a string"
            },
            "timestamp": {
              "bsonType": "date",
              "description": "Timestamp of the memory, required and must be a valid date"
            }
          }
        }
      },
      "sentiment_status": {
    "bsonType": "object",
    "required": ["sentiments", "reason"],
    "properties": {
      "sentiments": {
          "bsonType": "object",
          "required": [
            "affection",
            "trust",
            "admiration",
            "gratitude",
            "fondness",
            "respect",
            "comfort",
            "loyalty",
            "compassion",
            "appreciation",
            "warmth",
            "encouragement",
            "euphoria",
            "security",
            "excitement",
            "curiosity",
            "indifference",
            "ambivalence",
            "skepticism",
            "caution",
            "tolerance",
            "confusion",
            "neutrality",
            "boredom",
            "distrust",
            "resentment",
            "disdain",
            "envy",
            "frustration",
            "anger",
            "disappointment",
            "fear",
            "jealousy",
            "contempt",
            "irritation",
            "guilt",
            "regret",
            "suspicion",
            "hurt",
            "alienation",
            "disgust",
            "rejection",
            "sadness",
            "hostility",
            "embarrassment",
            "betrayal",
            "love",
            "attachment",
            "devotion",
            "obligation",
            "longing",
            "obsession",
            "protectiveness",
            "nostalgia",
            "pride",
            "vulnerability",
            "dependence",
            "insecurity",
            "possessiveness",
            "reverence",
            "pity",
            "relief",
            "inspiration",
            "admirationMixedWithEnvy",
            "guiltMixedWithAffection",
            "conflicted"
          ],
          "properties": {
            "affection": {
             
                "bsonType": "object",
                "required": ["description", "value", "min", "max"],
                "properties": {
                  "description": {
                    "bsonType": "string",
                    "description": "Warm, caring feelings towards someone. Required and must be a string."
                  },
                  "value": {
                    "bsonType": "int",
                    "description": "Current affection value. Must be an integer."
                  },
                  "min": {
                    "bsonType": "int",
                    "description": "Minimum value for affection. Must be an integer."
                  },
                  "max": {
                    "bsonType": "int",
                    "description": "Maximum value for affection. Must be an integer."
                  }
                }
              
            },
            "trust": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Confidence in someone’s reliability and integrity. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current trust value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for trust. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for trust. Must be an integer."
        }
      }
    
  },
  "admiration": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Respect or appreciation for someone's abilities or qualities. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current admiration value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for admiration. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for admiration. Must be an integer."
        }
      }
    
  },
  "gratitude": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Thankfulness for someone's help or kindness. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current gratitude value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for gratitude. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for gratitude. Must be an integer."
        }
      }
    
  },
  "fondness": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A gentle liking or affinity for someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current fondness value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for fondness. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for fondness. Must be an integer."
        }
      }
    
  },
  "respect": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "High regard for someone's qualities or achievements. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current respect value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for respect. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for respect. Must be an integer."
        }
      }
    
  },
  "comfort": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Feeling safe and secure with someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current comfort value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for comfort. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for comfort. Must be an integer."
        }
      }
    
  },
  "loyalty": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Dedication and allegiance to someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current loyalty value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for loyalty. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for loyalty. Must be an integer."
        }
      }
    
  },
  "compassion": {
    
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Deep sympathy and concern for someone’s suffering. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current compassion value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for compassion. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for compassion. Must be an integer."
        }
      }
    
  },
  "appreciation": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Recognizing someone's value or efforts. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current appreciation value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for appreciation. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for appreciation. Must be an integer."
        }
      }
    
  },
  "warmth": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A feeling of friendly or caring affection. Scale: 0 (no warmth) to 100 (deep warmth)."
        },
        "value": {
          "bsonType": "int",
          "description": "Current warmth value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for warmth. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for warmth. Must be an integer."
        }
      }
    
  },
  "encouragement": {
    
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Support and positive reinforcement of someone’s actions. Scale: 0 (no encouragement) to 100 (deep encouragement)."
        },
        "value": {
          "bsonType": "int",
          "description": "Current encouragement value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for encouragement. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for encouragement. Must be an integer."
        }
      }
    
  },
  "euphoria": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Intense happiness or joy related to someone. Scale: 0 (no euphoria) to 100 (extreme euphoria)."
        },
        "value": {
          "bsonType": "int",
          "description": "Current euphoria value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for euphoria. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for euphoria. Must be an integer."
        }
      }
    
  },
  "security": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A sense of safety and stability in someone's presence. Scale: 0 (no security) to 100 (extreme security)."
        },
        "value": {
          "bsonType": "int",
          "description": "Current security value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for security. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for security. Must be an integer."
        }
      }
    
  },
  "excitement": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Positive anticipation or thrill when thinking of someone. Scale: 0 (no excitement) to 100 (extreme excitement)."
        },
        "value": {
          "bsonType": "int",
          "description": "Current excitement value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for excitement. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for excitement. Must be an integer."
        }
      }
    
  },
  "curiosity": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Interest in learning more about someone. Scale: 0 (no curiosity) to 100 (intense curiosity)."
        },
        "value": {
          "bsonType": "int",
          "description": "Current curiosity value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for curiosity. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for curiosity. Must be an integer."
        }
      }
    
  },
  "indifference": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Lack of emotional investment or care for someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current indifference value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for indifference. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for indifference. Must be an integer."
        }
      }
    
  },
  "ambivalence": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Mixed or contradictory feelings toward someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current ambivalence value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for ambivalence. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for ambivalence. Must be an integer."
        }
      }
    
  },
  "skepticism": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Doubt about someone’s motives or reliability. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current skepticism value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for skepticism. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for skepticism. Must be an integer."
        }
      }
    
  },
  "caution": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Hesitation or wariness in trusting someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current caution value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for caution. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for caution. Must be an integer."
        }
      }
    
  },
  "tolerance": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Acceptance of someone without strong emotion, often despite differences. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current tolerance value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for tolerance. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for tolerance. Must be an integer."
        }
      }
    
  },
  "confusion": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Uncertainty or lack of understanding about someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current confusion value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for confusion. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for confusion. Must be an integer."
        }
      }
    
  },
  "neutrality": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "No particular emotional reaction or opinion about someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current neutrality value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for neutrality. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for neutrality. Must be an integer."
        }
      }
    
  },
  "boredom": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Disinterest or lack of stimulation from interactions with someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current boredom value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for boredom. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for boredom. Must be an integer."
        }
      }
    
  },
  "distrust": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Doubt in someone’s honesty or reliability. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current distrust value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for distrust. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for distrust. Must be an integer."
        }
      }
    
  },
  "resentment": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Bitterness or anger due to perceived mistreatment. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current resentment value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for resentment. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for resentment. Must be an integer."
        }
      }
    
  },
  "disdain": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Contempt or a sense of superiority over someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current disdain value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for disdain. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for disdain. Must be an integer."
        }
      }
    
  },
  "envy": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Discontentment due to someone else's advantages or success. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current envy value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for envy. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for envy. Must be an integer."
        }
      }
    
  },
  "frustration": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Annoyance or anger at someone's behavior. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current frustration value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for frustration. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for frustration. Must be an integer."
        }
      }
    
  },
  "anger": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Strong displeasure or hostility toward someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current anger value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for anger. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for anger. Must be an integer."
        }
      }
    
  },
  "disappointment": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Sadness due to unmet expectations in someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current disappointment value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for disappointment. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for disappointment. Must be an integer."
        }
      }
    
  },
  "fear": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Anxiety or apprehension about someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current fear value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for fear. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for fear. Must be an integer."
        }
      }
    
  },
  "jealousy": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Insecurity about someone taking away attention or affection. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current jealousy value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for jealousy. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for jealousy. Must be an integer."
        }
      }
    
  },
  "contempt": {
    
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Strong disapproval or lack of respect for someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current contempt value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for contempt. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for contempt. Must be an integer."
        }
      }
    
  },
  "irritation": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Mild annoyance at someone’s actions or words. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current irritation value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for irritation. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for irritation. Must be an integer."
        }
      }
    
  },
  "guilt": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A feeling of responsibility or remorse for wronging someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current guilt value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for guilt. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for guilt. Must be an integer."
        }
      }
    
  },
  "regret": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Sorrow or disappointment for past actions involving someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current regret value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for regret. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for regret. Must be an integer."
        }
      }
    
  },
  "suspicion": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Mistrust or doubt about someone’s true intentions. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current suspicion value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for suspicion. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for suspicion. Must be an integer."
        }
      }
    
  },
  "hurt": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Emotional pain caused by someone’s words or actions. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current hurt value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for hurt. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for hurt. Must be an integer."
        }
      }
    
  },
  "alienation": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Feeling disconnected or isolated from someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current alienation value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for alienation. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for alienation. Must be an integer."
        }
      }
    
  },
  "disgust": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Strong disapproval mixed with repulsion towards someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current disgust value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for disgust. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for disgust. Must be an integer."
        }
      }
    
  },
  "rejection": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Feeling cast aside or unwanted by someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current rejection value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for rejection. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for rejection. Must be an integer."
        }
      }
    
  },
  "sadness": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Emotional heaviness or grief due to someone’s actions or absence. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current sadness value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for sadness. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for sadness. Must be an integer."
        }
      }
    
  },
  "hostility": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Aggressive or antagonistic attitude toward someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current hostility value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for hostility. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for hostility. Must be an integer."
        }
      }
    
  },
  "embarrassment": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Feeling self-conscious or awkward due to someone’s actions. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current embarrassment value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for embarrassment. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for embarrassment. Must be an integer."
        }
      }
    
  },
  "betrayal": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A deep sense of violation of trust by someone close. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current betrayal value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for betrayal. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for betrayal. Must be an integer."
        }
      }
    
  },
  "love": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Deep, multifaceted affection, care, and attachment to someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current love value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for love. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for love. Must be an integer."
        }
      }
    
  },
  "attachment": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Emotional dependence and connection with someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current attachment value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for attachment. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for attachment. Must be an integer."
        }
      }
    
  },
  "devotion": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Strong loyalty and commitment, often marked by a willingness to sacrifice. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current devotion value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for devotion. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for devotion. Must be an integer."
        }
      }
    
  },
  "obligation": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A sense of responsibility to act or feel in a certain way toward someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current obligation value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for obligation. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for obligation. Must be an integer."
        }
      }
    
  },
  "longing": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Deep desire or yearning for someone, especially if separated. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current longing value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for longing. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for longing. Must be an integer."
        }
      }
    
  },
  "obsession": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Persistent preoccupation with someone, often unhealthy or intense. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current obsession value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for obsession. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for obsession. Must be an integer."
        }
      }
    
  },
  "protectiveness": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Strong desire to shield someone from harm or distress. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current protectiveness value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for protectiveness. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for protectiveness. Must be an integer."
        }
      }
    
  },
  "nostalgia": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Sentimentality for past experiences shared with someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current nostalgia value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for nostalgia. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for nostalgia. Must be an integer."
        }
      }
    
  },
  "pride": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Satisfaction in someone’s accomplishments or qualities. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current pride value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for pride. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for pride. Must be an integer."
        }
      }
    
  },
  "vulnerability": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Emotional openness and risk-taking in a relationship. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current vulnerability value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for vulnerability. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for vulnerability. Must be an integer."
        }
      }
    
  },
"dependence": {
   
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A reliance on someone for emotional support or fulfillment. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current dependence value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for dependence. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for dependence. Must be an integer."
        }
      }
    
  },
  "insecurity": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Doubts about one’s worth in someone’s eyes or in the relationship. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current insecurity value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for insecurity. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for insecurity. Must be an integer."
        }
      }
    
  },
  "possessiveness": {

      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Desire to control or have exclusive attention from someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current possessiveness value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for possessiveness. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for possessiveness. Must be an integer."
        }
      }
    
  },
  "reverence": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Deep respect mixed with awe for someone’s character or position. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current reverence value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for reverence. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for reverence. Must be an integer."
        }
      }
    
  },
  "pity": {
 
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Sympathy mixed with a sense of superiority, often toward someone in a difficult situation. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current pity value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for pity. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for pity. Must be an integer."
        }
      }
    
  },
  "relief": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "A sense of ease after resolving a conflict or misunderstanding with someone. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current relief value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for relief. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for relief. Must be an integer."
        }
      }
    
  },
  "inspiration": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Feeling motivated or uplifted by someone’s actions or words. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current inspiration value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for inspiration. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for inspiration. Must be an integer."
        }
      }
    
  },
  "admirationMixedWithEnvy": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Both respect and jealousy for someone’s accomplishments. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current admiration mixed with envy value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for admiration mixed with envy. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for admiration mixed with envy. Must be an integer."
        }
      }
    
  },
  "guiltMixedWithAffection": {
  
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Feeling regret for past wrongs but still caring for the person. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current guilt mixed with affection value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for guilt mixed with affection. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for guilt mixed with affection. Must be an integer."
        }
      }
    
  },
  "conflicted": {
      "bsonType": "object",
      "required": ["description", "value", "min", "max"],
      "properties": {
        "description": {
          "bsonType": "string",
          "description": "Experiencing competing sentiments, such as love mixed with distrust. Required and must be a string."
        },
        "value": {
          "bsonType": "int",
          "description": "Current conflicted value. Must be an integer."
        },
        "min": {
          "bsonType": "int",
          "description": "Minimum value for conflicted. Must be an integer."
        },
        "max": {
          "bsonType": "int",
          "description": "Maximum value for conflicted. Must be an integer."
        }
      }
  },      
          }
      },
      "reason": {
        "bsonType": "string",
        "description": "Reason for the sentiment status, optional and must be a string."
      }
    }
},
      "last_interaction": {
        "bsonType": "date",
        "description": "The timestamp of the user's last interaction, required and must be a valid date."
      }
    }
  }
}

MEMORY_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["agent_name", "event", "thoughts", "significance", "ts_created"],
        "additionalProperties": True,
        "properties": {
            "agent_name": {
                "bsonType": "string",
                "description": "Agent this memory belongs to"
            },
            "user": {
                "bsonType": ["string", "null"],
                "description": "Optional: username this memory is about"
            },
            "event": {
                "bsonType": "string",
                "description": "Brief event summary (what happened)"
            },
            "thoughts": {
                "bsonType": "string",
                "description": "Agent's internal reflection about the event"
            },
            "significance": {
                "enum": ["low", "medium", "high"],
                "description": "Use small discrete buckets for ranking/boosting"
            },
            "emotional_impact": {
                "bsonType": ["object", "null"],
                "additionalProperties": False,
                "properties": {
                    # keep lightweight; values mirror your 0..100 scales elsewhere
                    "joy":      {"bsonType": "object", "properties": {"value": {"bsonType": "int"}}},
                    "sadness":  {"bsonType": "object", "properties": {"value": {"bsonType": "int"}}},
                    "anger":    {"bsonType": "object", "properties": {"value": {"bsonType": "int"}}},
                    "fear":     {"bsonType": "object", "properties": {"value": {"bsonType": "int"}}},
                    "surprise": {"bsonType": "object", "properties": {"value": {"bsonType": "int"}}},
                    "love":     {"bsonType": "object", "properties": {"value": {"bsonType": "int"}}},
                    "disgust":  {"bsonType": "object", "properties": {"value": {"bsonType": "int"}}}
                }
            },
            "tags": {
                "bsonType": ["array", "null"],
                "items": {"bsonType": "string"},
                "description": "Keyword/topic tags"
            },
            "embedding": {
                "bsonType": ["array", "null"],
                "items": {"bsonType": "double"},
                "description": "Vector embedding for semantic search (optional)"
            },
            "recall_count": {
                "bsonType": "int",
                "description": "Times this memory was retrieved",
                "minimum": 0
            },
            "ts_created": {
                "bsonType": "date",
                "description": "Creation timestamp (UTC)"
            },
            "ts_last_accessed": {
                "bsonType": ["date", "null"],
                "description": "Last time the memory was retrieved"
            },
            "ttl_at": {
                "bsonType": ["date", "null"],
                "description": "Optional: time to expire low-value memories"
            }
        }
    }
}

