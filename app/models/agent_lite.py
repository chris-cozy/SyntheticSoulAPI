
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
        } ,
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