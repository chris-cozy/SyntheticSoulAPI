
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
