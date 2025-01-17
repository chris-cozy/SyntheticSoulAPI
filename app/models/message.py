
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
