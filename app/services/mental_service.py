import os
from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Any
from typing import Dict, Any
from datetime import datetime
from app.constants.schemas import get_emotion_status_schema, get_extrinsic_relationship_schema, get_identity_schema, get_message_schema, get_personality_status_schema, get_response_choice_schema, get_sentiment_status_schema, get_summary_schema
from app.models.conversations import MessageSchema
from app.models.request import MessageRequest
from app.services.openai_service import get_structured_query_response 
import json
from app.constants.constants import CONVERSATION_MESSAGE_RETENTION_COUNT, EXTRINSIC_RELATIONSHIPS, MAX_SENTIMENT_VALUE, MIN_PERSONALITY_VALUE, MAX_PERSONALITY_VALUE, MIN_SENTIMENT_VALUE
from app.models.memory import SelfSchema, UserSchema
from app.services.openai_service import get_structured_query_response
from app.services.data_service import grab_user, grab_self, get_conversation, get_database, db_client
from dotenv import load_dotenv

load_dotenv()


    
async def process_message(request: MessageRequest):
        """
        Process a user message and return the bot's response.

        :param request: Request containing user_id and message content
        :return: JSON response with the bot's reply
        """
        if not db_client:
            raise RuntimeError("Database client is not initialized. Ensure `init_db()` is called successfully.")

        try:
            db = get_database()

            # Step 1: Fetch user and self objects
            self = await grab_self(os.getenv("BOT_NAME"))
            user = await grab_user(request.user_id, request.user_name)
            conversation = await get_conversation(request.user_id)
            recent_messages = conversation["messages"][-CONVERSATION_MESSAGE_RETENTION_COUNT:] if "messages" in conversation else []
            received_date = datetime.now() 

            # Step 2: Prepare ongoing conversation context
            ongoing_conversation_string = (
                f"This is what {self['name']} remembers of the conversation between them and {user['name']}: ({json.dumps(recent_messages)})."
                if recent_messages
                else f"This is {self['name']}'s and {user['name']}'s first time talking."
            )

            # Step 3: Define relationship context
            intrinsic_relationship = (
                f"{user['name']} is {self['name']}'s {user['intrinsic_relationship']}."
                if user["intrinsic_relationship"] == "creator and master"
                else f"There is no intrinsic relationship between {self['name']} and {user['name']}."
            )

            extrinsic_relationship = f"{self['name']} has an extrinsic relationship with {user['name']} of {user['extrinsic_relationship']}."

            # Step 4: Update personality based on relationships
            altered_personality = await alter_personality(self, user, extrinsic_relationship)

            self_context = (
            f"{self['name']}'s current activity is {self['activity_status']}. Their current personality traits are: ({altered_personality}). {self['name']}'s current emotional state is ({self['emotional_status']})."
            )

            # Step 5: Query OpenAI for emotional state changes
            initial_emotion_query = {
                "role": "user",
                "content": (
                    f"{self_context} This is what {self['name']} has learned about {user['name']}: {user['summary']}. {intrinsic_relationship} {extrinsic_relationship} {ongoing_conversation_string} It is {received_date}. {user['name']} just sent a message to {self['name']}: {request.message}. How would this alter {self['name']}'s emotional state? Provide the new object (only the emotions whose value properties have changed, whether increased or decreased), and the reason behind the current emotional state."
                ),
            }

            inner_dialogue = [initial_emotion_query]
            initial_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema())

            if not initial_emotion_response:
                raise HTTPException(status_code=500, detail="Error processing emotional reaction")
            
            db["selves"].update({"discord_id": self["discord_id"]}, { "$set": {"emotional_status": deep_merge(self["emotional_status"], initial_emotion_response) }})

            # Step 6: Analyze the purpose and tone of the user's message
            message_queries = [{
                "role": "user",
                "content": (
                    f"This is {self['name']}'s personality: ({altered_personality}). This is their current emotional state: ({self['emotional_status']}). This is what they think about {user['name']}: {user['summary']}. {intrinsic_relationship} {extrinsic_relationship}. This is the ongoing conversation between them: ({ongoing_conversation_string}). How would {self['name']} perceive the purpose and tone of {user['name']}'s new message: {request.message}?"
                ),
            }]

            message_analysis = await get_structured_query_response(message_queries, get_message_schema())

            if not message_analysis:
                raise HTTPException(status_code=500, detail="Error analyzing user message")
            
            message_queries.append(message_analysis)
            
            # Step 7: Determine whether to respond
            response_choice_query = {
                "role": "user",
                "content": (
                    f"{self['name']} can choose to respond to or ignore this message. Based on their personality, current emotional state, and thoughts on {user['name']}, what choice will they make? Provide either 'respond' or 'ignore', and the reason for the choice."
                ),
            }

            message_queries.append(response_choice_query)

            response_choice = await get_structured_query_response(message_queries, get_response_choice_schema())

            if not message_analysis:
                raise HTTPException(status_code=500, detail="Error generating response choice")
            
            message_queries.append(response_choice)


#####################################
            if response_choice["response_choice"] == "respond":
                # Craft response
                response_query = {
                    "role": "user",
                    "content": (
                        f"The way {self['name']} communicates reflects their personality traits: ({altered_personality}), and current emotional status: ({self['emotional_status']}). How would {self['name']} respond back, and with what intended purpose and tone?"
                    ),
                }

                message_queries.append(response_query)
                response_content = await get_structured_query_response(message_queries, get_message_schema())

                if not response_content:
                    raise HTTPException(status_code=500, detail="Error generating response")
                
                # Reflection: Evaluate bot's emotional state after responding
                final_emotion_query = {
                    "role": "user",
                    "content": (
                        f"{self['name']} responded with this message: {response_content}. What is {self['name']}'s emotional state after sending their response? Provide the new object (only the emotions whose value properties have changed, whether increased or decreased) and the reason behind the current emotional state. Scale: {MIN_SENTIMENT_VALUE} (lowest intensity) to {MAX_SENTIMENT_VALUE} (highest intensity)."
                    ),
                }

                # Add the query to the inner dialogue
                inner_dialogue.append(final_emotion_query)

                final_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema())

                # Handle errors if the emotional response is not received
                if not final_emotion_response:
                    raise HTTPException(status_code=500, detail="Error reflecting on emotion")

                # Add the response to the dialogue history
                inner_dialogue.append({
                    "role": "assistant",
                    "content": json.dumps(final_emotion_response),
                })

            
                # Update the bot's emotional status
                self["emotional_status"].update(deep_merge(self["emotional_status"], final_emotion_response))

            elif response_choice["response_choice"] == "ignore":
                # Reflection: Evaluate bot's emotional state after ignoring the message
                final_emotion_query = {
                    "role": "user",
                    "content": (
                        f"What is {self['name']}'s emotional state after ignoring the message? "
                        f"Provide the new object (only the emotions whose value properties have changed, whether increased or decreased), "
                        f"and the reason behind the current emotional state. Scale: {MIN_SENTIMENT_VALUE} (lowest intensity) "
                        f"to {MAX_SENTIMENT_VALUE} (highest intensity)."
                    ),
                }

                # Add the query to the inner dialogue
                inner_dialogue.append(final_emotion_query)

                final_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema())

                # Handle errors if the emotional response is not received
                if not final_emotion_response:
                    raise HTTPException(status_code=500, detail="Error reflecting on emotion")

                # Add the response to the dialogue history
                inner_dialogue.append({
                    "role": "assistant",
                    "content": json.dumps(final_emotion_response),
                })

                

                # Update the bot's emotional status
                self["emotional_status"].update(deep_merge(self["emotional_status"], final_emotion_response))

            # Sentiment Reflection
            sentiment_query = {
                "role": "user",
                "content": (
                    f"What are {self['name']}'s sentiments towards {user['name']} after this message exchange? "
                    f"Provide the new object (only the sentiments whose value properties have changed, whether increased or decreased), "
                    f"and the updated reason behind the current sentiment. Scale: {MIN_SENTIMENT_VALUE} (lowest intensity) "
                    f"to {MAX_SENTIMENT_VALUE} (highest intensity)."
                ),
            }

            inner_dialogue.append(sentiment_query)

            sentiment_response = await get_structured_query_response(inner_dialogue, get_sentiment_status_schema())

            if not sentiment_response:
                raise HTTPException(status_code=500, detail="Error reflecting on sentiment")

            inner_dialogue.append({
                "role": "assistant",
                "content": json.dumps(sentiment_response),
            })

            # Update user sentiment status
            user["sentiment_status"].update(sentiment_response)

            # Summary Reflection
            summary_query = {
                "role": "user",
                "content": (
                    f"Add any new key information {self['name']} has learned about {user['name']} from this message exchange, "
                    f"to the summary of what they know about {user['name']}: {user['summary']}. "
                    "Then re-summarize everything for brevity. Provide the updated summary in a JSON object with the property 'summary'."
                ),
            }

            inner_dialogue.append(summary_query)

            summary_response = await get_structured_query_response(inner_dialogue, get_summary_schema())

            if not summary_response:
                raise HTTPException(status_code=500, detail="Error reflecting on summary")

            inner_dialogue.append({
                "role": "assistant",
                "content": json.dumps(summary_response),
            })

            # Update user summary
            user["summary"] = summary_response["summary"]

            # Extrinsic Relationship Reflection
            extrinsic_relationship_query = {
                "role": "user",
                "content": (
                    f"Has the extrinsic relationship of {user['name']} changed? Whether it has changed or not, provide the extrinsic "
                    f"relationship out of these options {EXTRINSIC_RELATIONSHIPS} in a JSON object with the property 'extrinsic_relationship'."
                ),
            }

            inner_dialogue.append(extrinsic_relationship_query)

            extrinsic_relationship_response = await get_structured_query_response(inner_dialogue, get_extrinsic_relationship_schema())

            if not extrinsic_relationship_response:
                raise HTTPException(status_code=500, detail="Error reflecting on extrinsic relationship")

            inner_dialogue.append({
                "role": "assistant",
                "content": json.dumps(extrinsic_relationship_response),
            })

            # Update user's extrinsic relationship
            user["extrinsic_relationship"] = extrinsic_relationship_response["extrinsic_relationship"]

            # Self-Identity Reflection
            identity_query = {
                "role": "user",
                "content": (
                    f"Add any new information {self['name']} has learned about themselves from this message exchange, "
                    f"to their current self-identity {self['identity']}. "
                    "Then re-summarize everything for brevity. Provide the updated identity in a JSON object with the property 'identity'."
                ),
            }

            inner_dialogue.append(identity_query)

            identity_response = await get_structured_query_response(inner_dialogue, get_identity_schema())

            if not identity_response:
                raise HTTPException(status_code=500, detail="Error reflecting on self-identity")

            inner_dialogue.append({
                "role": "assistant",
                "content": json.dumps(identity_response),
            })


            # Update bot's self-identity
            self["identity"] = identity_response["identity"]

            # Update and Save Conversation
            incoming_message = MessageSchema(
                message=message_analysis["message"],
                purpose=message_analysis["purpose"],
                tone=message_analysis["tone"],
                sender=user["name"],
                is_bot=False
            )
            conversation["messages"].append(incoming_message)

            if response_choice["response_choice"] == "respond":
                response_date = datetime.utcnow()
                bot_response_message = MessageSchema(
                    message=response_content["message"],
                    purpose=response_content["purpose"],
                    tone=response_content["tone"],
                    sender=self["name"],
                    is_bot=True
                )
                conversation["messages"].append(bot_response_message)
                return {"response": response_content["message"]}

            elif response_choice["response_choice"] == "ignore":
                return {"response": f"System: {self['name']} has chosen to ignore your message."}

            # Update user and conversation in database
            user["last_interaction"] = datetime.now()

        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
async def alter_personality(self: SelfSchema, user: UserSchema, extrinsic_relationship: str):
    """
    Alters the bot's personality based on the user's sentiment status and their extrinsic relationship.

    :param self: The self (bot) object
    :param user: The user object
    :param extrinsic_relationship_string: String describing the extrinsic relationship
    :return: New personality object
    """
    personality = self["personality_matrix"]
    sentiment = user["sentiment_status"]

    alter_query = [
        {
        "role": "user",
        "content": (
            f"These are {self['name']}'s personality traits: {json.dumps(personality)}. "
            f"These are {self['name']}'s sentiments towards {user['name']}: {sentiment}. "
            f"How would these sentiments and extrinsic relationship ({extrinsic_relationship}) alter {self['name']}'s personality when interacting with {user['name']}? "
            f"Provide the new object (only the personality traits whose value properties have changed, whether increased or decreased). "
            f"Scale: {MIN_PERSONALITY_VALUE} (lowest intensity) to {MAX_PERSONALITY_VALUE} (highest intensity)."
            ),
        }
    ]
     
    alter_query_response = await get_structured_query_response(alter_query, get_personality_status_schema())

    # Merge the response with the original personality matrix
    altered_personality = deep_merge(personality, alter_query_response)

    return altered_personality

def deep_merge(target: Dict[str, Any], source: Dict[str, Any], average: bool = False) -> Dict[str, Any]:
    """
    Recursively merges the property values of the source object into the target object.

    :param target: Target object (dict)
    :param source: Source object (dict)
    :param average: Whether to average values when merging
    :return: Updated target object
    """
    for key, value in source.items():
        if isinstance(value, dict) and key in target:
            target[key] = deep_merge(target[key], value, average)
        else:
            if average and key in target:
                target[key] = (target[key] + value) / 2
            else:
                target[key] = value
    return target