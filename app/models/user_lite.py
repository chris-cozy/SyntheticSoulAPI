
USER_LITE_VALIDATOR = {

    "bsonType": "object",
    "required": [
      "username",
      "agent_perspective"
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
          "creator and master",
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