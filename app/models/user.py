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



