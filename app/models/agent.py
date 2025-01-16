
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



