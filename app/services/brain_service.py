import asyncio
import os
from fastapi import HTTPException
from typing import Dict, Any
from typing import Dict, Any
from datetime import datetime
from app.constants.schemas import get_emotion_status_schema, get_extrinsic_relationship_schema, get_identity_schema, get_message_schema, get_personality_status_schema, get_response_choice_schema, get_sentiment_status_schema, get_summary_schema, get_thought_schema, implicitly_addressed_schema
from app.constants.schemas_lite import get_emotion_status_schema_lite, get_personality_status_schema_lite, get_sentiment_status_schema_lite
from app.models.request import ImplicitlyAddressedResponse, MessageRequest, MessageResponse
from app.services.openai_service import get_structured_query_response 
import json
from app.constants.constants import AGENT_COLLECTION, AGENT_LITE_COLLECTION, AGENT_NAME_PROPERTY, BOT_ROLE, CONVERSATION_COLLECTION, CONVERSATION_MESSAGE_RETENTION_COUNT, EXTRINSIC_RELATIONSHIPS, IGNORE_CHOICE, MAX_EMOTION_VALUE, MAX_SENTIMENT_VALUE, MESSAGE_HISTORY_COUNT, MIN_EMOTION_VALUE, MIN_PERSONALITY_VALUE, MAX_PERSONALITY_VALUE, MIN_SENTIMENT_VALUE, PERSONALITY_LANGUAGE_GUIDE, RESPOND_CHOICE, SYSTEM_MESSAGE, THINKING_RATE, USER_COLLECTION, USER_LITE_COLLECTION, USER_NAME_PROPERTY, USER_ROLE
from app.services.openai_service import get_structured_query_response
from app.services.data_service import get_message_memory, grab_user, grab_self, get_conversation, get_database, insert_message_to_memory
from dotenv import load_dotenv

from app.services.prompt_service import generate_extrinsic_relationship_prompt, generate_final_emotional_response_prompt, generate_identity_update_prompt, generate_initial_emotional_response_prompt, generate_message_perception_prompt, generate_personality_adjustment_prompt, generate_response_analysis_prompt, generate_response_choice_prompt, generate_sentiment_analysis_prompt, generate_summary_update_prompt, generate_thought_prompt

agent_name = os.getenv("BOT_NAME")

load_dotenv()

async def check_implicit_addressing(request: MessageRequest):
    """Checks if the agent is being implicitly addressed

    Args:
        request (MessageRequest): message request

    Raises:
        HTTPException: Error - check_implicit_addressing

    Returns:
        ImplicitlyAddressedResponse: Whether the bot has been implicitly addressed
    """
    agent_name = os.getenv("BOT_NAME")

    message_memory = await get_message_memory(agent_name, MESSAGE_HISTORY_COUNT)

    new_message_request = {
            "message": request.message,
            "sender": request.username,
            "timestamp": datetime.now()
            }
            
    await insert_message_to_memory(agent_name, new_message_request)

    try:
        query = {
            "role": "user",
            "content": (
                f"Analyze the conversation history ({message_memory}) and determine if the most recent message ({request}) implicitly addresses {agent_name}. Provide your output in this JSON structure:{{\"implicitly_addressed\": 'yes' or 'no'}}"
            )
        }

        result = await get_structured_query_response([query], implicitly_addressed_schema())
        if not result:
            raise HTTPException(status_code=500, detail="Error - check_implicit_addressing")
        
        return ImplicitlyAddressedResponse(implicitly_addressed=result["implicitly_addressed"])
    except Exception as e:
        print(e)

async def send_message(request: MessageRequest):
    """
    Selects whether to process the message in lite mode or not

    Args:
        request (MessageRequest): message request
    """
    lite_mode = True

    if(lite_mode):
        response = await process_message_lite(request)
    else:
        response = await process_message(request)
    
    return response

async def process_message(request: MessageRequest):
        """
        Process a user message and return the bot's response.

        :param request: Request containing user_id and message content
        :return: JSON response with the bot's reply
        """
        try:
            db = get_database()

            # Step 1: Fetch user and self objects: CLEAR
            self = await grab_self(os.getenv("BOT_NAME"), False)
            user = await grab_user(request.username, os.getenv("BOT_NAME"), False)

            conversation = await get_conversation(user[USER_NAME_PROPERTY], self[AGENT_NAME_PROPERTY])
            recent_messages = conversation["messages"][-CONVERSATION_MESSAGE_RETENTION_COUNT:] if "messages" in conversation else []
            received_date = datetime.now() 

            # Step 2: Prepare ongoing conversation context: CLEAR
            ongoing_conversation_string = (
                f"This is what {self[AGENT_NAME_PROPERTY]} remembers of the conversation between them and {user[USER_NAME_PROPERTY]}: ({recent_messages})."
                if recent_messages
                else f"This is {self[AGENT_NAME_PROPERTY]}'s and {user[USER_NAME_PROPERTY]}'s first time talking."
            )

            # Step 3: Define relationship context
            intrinsic_relationship = (
                f"{user[USER_NAME_PROPERTY]} is {self[AGENT_NAME_PROPERTY]}'s {user['intrinsic_relationship']}."
                if user["intrinsic_relationship"] == "creator and master"
                else f"There is no intrinsic relationship between {self[AGENT_NAME_PROPERTY]} and {user[USER_NAME_PROPERTY]}."
            )

            extrinsic_relationship = f"{self[AGENT_NAME_PROPERTY]} has an extrinsic relationship with {user[USER_NAME_PROPERTY]} of {user['extrinsic_relationship']}."

            # Step 4: Update personality based on relationships: CLEAR
            altered_personality = await alter_personality(self, user, extrinsic_relationship, False)

            self_context = (
            f"{self[AGENT_NAME_PROPERTY]}'s current personality traits are: ({altered_personality}). {self[AGENT_NAME_PROPERTY]}'s current emotional state is ({self['emotional_status']})."
            )

            # Step 5: Query ai service for emotional state changes: CLEAR
            initial_emotion_query = {
                "role": "user",
                "content": (
                    f"{self_context} This is what {self[AGENT_NAME_PROPERTY]} has learned about {user[USER_NAME_PROPERTY]}: {user['summary']}. {intrinsic_relationship} {extrinsic_relationship} {ongoing_conversation_string} It is {received_date}. {user[USER_NAME_PROPERTY]} just sent a message to {self[AGENT_NAME_PROPERTY]}: {request.message}. How would this alter {self[AGENT_NAME_PROPERTY]}'s emotional state? Provide the new object (only the emotions whose value properties have changed, whether increased or decreased), and the reason behind the current emotional state. Scale:{MIN_SENTIMENT_VALUE} (lowest intensity) to {MAX_SENTIMENT_VALUE} (highest intensity). Do not add new emotions."
                ),
            }

            inner_dialogue = [initial_emotion_query]
            initial_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema())

            if not initial_emotion_response:
                raise HTTPException(status_code=500, detail="Error processing emotional reaction")
            
            inner_dialogue.append({
                "role": BOT_ROLE,
                "content": json.dumps(initial_emotion_response)
                })
            
            current_emotions = deep_merge(self["emotional_status"], initial_emotion_response)

            db[AGENT_COLLECTION].update_one({"name": self[AGENT_NAME_PROPERTY]}, { "$set": {"emotional_status": current_emotions }})

            # Step 6: Analyze the purpose and tone of the user's message: CLEAR
            message_queries = [{
                "role": "user",
                "content": (
                    f"This is {self[AGENT_NAME_PROPERTY]}'s personality: ({altered_personality}). This is their current emotional state: ({self['emotional_status']}). This is what they think about {user[USER_NAME_PROPERTY]}: {user['summary']}. {intrinsic_relationship} {extrinsic_relationship}. This is the ongoing conversation between them: ({ongoing_conversation_string}). How would {self[AGENT_NAME_PROPERTY]} perceive the purpose and tone of {user[USER_NAME_PROPERTY]}'s new message: ({request.message})? Provide the message ({request.message}), purpose, and tone in a JSON object with the properties of message, purpose, and tone."
                ),
            }]

            message_analysis = await get_structured_query_response(message_queries, get_message_schema())

            if not message_analysis:
                raise HTTPException(status_code=500, detail="Error analyzing user message")
            
            message_queries.append({
                "role": BOT_ROLE,
                "content": json.dumps(message_analysis)
                })
        
            # Step 7: Determine whether to respond: CLEAR
            response_choice_query = {
                "role": "user",
                "content": (
                    f"{self[AGENT_NAME_PROPERTY]} can choose to respond to or ignore this message. Based on their personality, current emotional state, and thoughts on {user[USER_NAME_PROPERTY]}, what choice will they make? Provide either 'respond' or 'ignore', and the reason for the choice, in a JSON object with the properties response_choice and reason."
                ),
            }

            message_queries.append(response_choice_query)

            response_choice = await get_structured_query_response(message_queries, get_response_choice_schema())

            if not response_choice:
                raise HTTPException(status_code=500, detail="Error generating response choice")
            
            message_queries.append({
                "role": BOT_ROLE,
                "content": json.dumps(response_choice)
                })
            
            if response_choice["response_choice"] == RESPOND_CHOICE:
                #Step 8: Generate a response: CLEAR
                response_query = {
                    "role": USER_ROLE,
                    "content": (
                        f"The way {self[AGENT_NAME_PROPERTY]} communicates reflects their personality traits: ({altered_personality}), and current emotional status: ({self['emotional_status']}). How would {self[AGENT_NAME_PROPERTY]} respond back, and with what intended purpose and tone? Provide the response, intended purpose, and intended tone in a JSON object with the properties of message, purpose, and tone."
                    ),
                }

                message_queries.append(response_query)
                response_content = await get_structured_query_response(message_queries, get_message_schema())

                if not response_content:
                    raise HTTPException(status_code=500, detail="Error generating response")
                
                # Step 9: Evaluate bot's emotional state after responding: CLEAR
                final_emotion_query = {
                    "role": USER_ROLE,
                    "content": (
                        f"{self[AGENT_NAME_PROPERTY]} responded with this message: ({response_content}). What is {self[AGENT_NAME_PROPERTY]}'s emotional state after sending their response? Provide the new object (only the emotions whose value properties have changed, whether increased or decreased) and the reason behind the current emotional state. Scale: {MIN_SENTIMENT_VALUE} (lowest intensity) to {MAX_SENTIMENT_VALUE} (highest intensity). Do not add new emotions."
                    ),
                }

                inner_dialogue.append(final_emotion_query)

                final_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema())

                if not final_emotion_response:
                    raise HTTPException(status_code=500, detail="Error reflecting on emotion")

                inner_dialogue.append({
                    "role": BOT_ROLE,
                    "content": json.dumps(final_emotion_response),
                })

            
                current_emotions = deep_merge(self["emotional_status"], final_emotion_response)

                db[AGENT_COLLECTION].update_one({"name": self[AGENT_NAME_PROPERTY]}, { "$set": {"emotional_status": current_emotions }})

            elif response_choice["response_choice"] == IGNORE_CHOICE:
                # Step 8-9: Evaluate bot's emotional state after ignoring the message: CLEAR
                final_emotion_query = {
                    "role": USER_ROLE,
                    "content": (
                        f"What is {self[AGENT_NAME_PROPERTY]}'s emotional state after ignoring the message? Provide the new object (only the emotions whose value properties have changed, whether increased or decreased), and the reason behind the current emotional state. Scale: {MIN_SENTIMENT_VALUE} (lowest intensity) to {MAX_SENTIMENT_VALUE} (highest intensity). Do not add new emotions."
                    ),
                }

                inner_dialogue.append(final_emotion_query)

                final_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema())

                if not final_emotion_response:
                    raise HTTPException(status_code=500, detail="Error reflecting on emotion")

                inner_dialogue.append({
                    "role": BOT_ROLE,
                    "content": json.dumps(final_emotion_response),
                })

                current_emotions = deep_merge(self["emotional_status"], final_emotion_response)
                db[AGENT_COLLECTION].update_one({"name": self[AGENT_NAME_PROPERTY]}, { "$set": {"emotional_status": current_emotions }})

            # Step 10: Sentiment Reflection: CLEAR
            sentiment_query = {
                "role": USER_ROLE,
                "content": (
                    f"What are {self[AGENT_NAME_PROPERTY]}'s sentiments towards {user[USER_NAME_PROPERTY]} after this message exchange? Provide the new object (only the sentiments whose value properties have changed, whether increased or decreased), and the updated reason behind the current sentiment. Scale: {MIN_SENTIMENT_VALUE} (lowest intensity) to {MAX_SENTIMENT_VALUE} (highest intensity). Do not add new sentiments."
                ),
            }

            inner_dialogue.append(sentiment_query)

            sentiment_response = await get_structured_query_response(inner_dialogue, get_sentiment_status_schema())

            if not sentiment_response:
                raise HTTPException(status_code=500, detail="Error reflecting on sentiment")

            inner_dialogue.append({
                "role": BOT_ROLE,
                "content": json.dumps(sentiment_response),
            })

            current_sentiments = deep_merge(user["sentiment_status"], sentiment_response)

            db[USER_COLLECTION].update_one({USER_NAME_PROPERTY: user[USER_NAME_PROPERTY]}, { "$set": {"sentiment_status": current_sentiments }})

            #Step 11:  Summary Reflection: CLEAR
            summary_query = {
                "role": USER_ROLE,
                "content": (
                    f"Add any new key information {self[AGENT_NAME_PROPERTY]} has learned about {user[USER_NAME_PROPERTY]} from this message exchange, to the summary of what they know about {user[USER_NAME_PROPERTY]}: {user['summary']}. Then re-summarize everything for brevity. Provide the updated summary in a JSON object with the property 'summary'."
                ),
            }

            inner_dialogue.append(summary_query)

            summary_response = await get_structured_query_response(inner_dialogue, get_summary_schema())

            if not summary_response:
                raise HTTPException(status_code=500, detail="Error reflecting on summary")

            inner_dialogue.append({
                "role": BOT_ROLE,
                "content": json.dumps(summary_response),
            })

            db[USER_COLLECTION].update_one({USER_NAME_PROPERTY: user[USER_NAME_PROPERTY]}, { "$set": {"summary": summary_response["summary"] }})

            #Step 12: Extrinsic Relationship Reflection: CLEAR
            extrinsic_relationship_query = {
                "role": USER_ROLE,
                "content": (
                    f"Has the extrinsic relationship of {user[USER_NAME_PROPERTY]} changed? Whether it has changed or not, provide the extrinsic relationship out of these options ({EXTRINSIC_RELATIONSHIPS}) in a JSON object with the property 'extrinsic_relationship'."
                ),
            }

            inner_dialogue.append(extrinsic_relationship_query)

            extrinsic_relationship_response = await get_structured_query_response(inner_dialogue, get_extrinsic_relationship_schema())

            if not extrinsic_relationship_response:
                raise HTTPException(status_code=500, detail="Error reflecting on extrinsic relationship")

            inner_dialogue.append({
                "role": BOT_ROLE,
                "content": json.dumps(extrinsic_relationship_response),
            })

            db[USER_COLLECTION].update_one({USER_NAME_PROPERTY: user[USER_NAME_PROPERTY]}, { "$set": {"extrinsic_relationship": extrinsic_relationship_response["extrinsic_relationship"] }})

            #Step 13: Self-Identity Reflection: CLEAR
            identity_query = {
                "role": USER_ROLE,
                "content": (
                    f"Add any new information {self[AGENT_NAME_PROPERTY]} has learned about themselves from this message exchange, to their current self-identity {self['identity']}. Then re-summarize everything for brevity. Provide the updated identity in a JSON object with the property 'identity'."
                ),
            }

            inner_dialogue.append(identity_query)

            identity_response = await get_structured_query_response(inner_dialogue, get_identity_schema())

            if not identity_response:
                raise HTTPException(status_code=500, detail="Error reflecting on self-identity")

            inner_dialogue.append({
                "role": BOT_ROLE,
                "content": json.dumps(identity_response),
            })

            db[AGENT_COLLECTION].update_one({AGENT_NAME_PROPERTY: self[AGENT_NAME_PROPERTY]}, { "$set": {"identity": identity_response["identity"] }})

        
            # Update and Save Conversation
            incoming_message = {
                "message": message_analysis["message"],
                "purpose": message_analysis["purpose"],
                "tone": message_analysis["tone"],
                "timestamp": datetime.now(),
                "sender": user[USER_NAME_PROPERTY],
                "from_agent": False
            }

            conversation["messages"].append(incoming_message)

            db[CONVERSATION_COLLECTION].update_one({USER_NAME_PROPERTY: user[USER_NAME_PROPERTY], "agent_name": self[AGENT_NAME_PROPERTY]}, { "$set": {"messages": conversation["messages"] }})


            if response_choice["response_choice"] == RESPOND_CHOICE:
                bot_response_message = {
                    "message": response_content["message"],
                    "purpose": response_content["purpose"],
                    "tone": response_content["tone"],
                    "timestamp": datetime.now(),
                    "sender": self[AGENT_NAME_PROPERTY],
                    "from_agent": True
                }
            
                conversation["messages"].append(bot_response_message)
                db[CONVERSATION_COLLECTION].update_one({USER_NAME_PROPERTY: user[USER_NAME_PROPERTY], "agent_name": self[AGENT_NAME_PROPERTY]}, { "$set": {"messages": conversation["messages"] }})

                db[USER_COLLECTION].update_one({USER_NAME_PROPERTY: user[USER_NAME_PROPERTY]}, { "$set": {"last_interaction": datetime.now() }})

                return MessageResponse(response = response_content["message"])

            elif response_choice["response_choice"] == IGNORE_CHOICE:

                db[USER_COLLECTION].update_one({USER_NAME_PROPERTY: user[USER_NAME_PROPERTY]}, { "$set": {"last_interaction": datetime.now() }})

                return MessageResponse({"response": f"System: {self[AGENT_NAME_PROPERTY]} has chosen to ignore your message."})
            
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

async def process_message_lite(request: MessageRequest):
        """
        Process a user message and return the bot's response. LITE VERSION

        :param request: Request containing user_id and message content
        :return: JSON response with the bot's reply
        """
        try:        
            db = get_database()
            
            user_lite_collection = db[USER_LITE_COLLECTION]
            username = request.username

            # Step 1: Fetch user and self objects: CLEAR
            recent_all_messages = await get_message_memory(agent_name, MESSAGE_HISTORY_COUNT)
            self = await grab_self(agent_name, True)  
            user = await grab_user(username, agent_name, True)
            conversation = await get_conversation(username, agent_name)
            recent_messages = conversation["messages"][-CONVERSATION_MESSAGE_RETENTION_COUNT:] if "messages" in conversation else []
            received_date = datetime.now() 

            # Step 4: Update personality based on relationships: CLEAR
            altered_personality = await alter_personality(self, user, True)
            
            inner_dialogue = [SYSTEM_MESSAGE]
            
            # Step 5: Query ai service for emotional state changes: CLEAR
            initial_emotion_query = {
                "role": "user",
                "content": (generate_initial_emotional_response_prompt(agent_name, altered_personality, self['emotional_status'], username, user['summary'], user["intrinsic_relationship"], user['extrinsic_relationship'], recent_messages, recent_all_messages, received_date, request.message, MIN_EMOTION_VALUE, MAX_EMOTION_VALUE, self['thoughts'][-1])),
            }

            inner_dialogue.append(initial_emotion_query)
            initial_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema_lite())

            if not initial_emotion_response:
                raise HTTPException(status_code=500, detail="Error - process_message_lite: Processing initial emotional reaction")
            
            inner_dialogue.append({
                "role": BOT_ROLE,
                "content": json.dumps(initial_emotion_response)
                })

            current_emotions = deep_merge(self["emotional_status"], initial_emotion_response)

            # Step 6: Analyze the purpose and tone of the user's message: CLEAR
            message_queries = [SYSTEM_MESSAGE, {
                "role": "user",
                "content": (
                    generate_message_perception_prompt(agent_name, altered_personality, current_emotions, username, user['summary'], user["intrinsic_relationship"], user['extrinsic_relationship'], recent_messages, recent_all_messages, request.message)
                ),
            }]
            
            message_analysis = await get_structured_query_response(message_queries, get_message_schema())

            if not message_analysis:
                raise HTTPException(status_code=500, detail="Error - process_message_lite: analyzing user message")
            
            message_queries.append({
                "role": BOT_ROLE,
                "content": json.dumps(message_analysis)
                })
        
            # Step 7: Determine whether to respond: CLEAR
            response_choice_query = {
                "role": "user",
                "content": (
                    generate_response_choice_prompt(agent_name, username)
                ),
            }
            
            message_queries.append(response_choice_query)

            response_choice = await get_structured_query_response(message_queries, get_response_choice_schema())

            if not response_choice:
                raise HTTPException(status_code=500, detail="Error - process_message_lite: generating response choice")
            
            message_queries.append({
                "role": BOT_ROLE,
                "content": json.dumps(response_choice)
                })
            
            if response_choice["response_choice"] == RESPOND_CHOICE:
                #Step 8: Generate a response: CLEAR
                response_query = {
                    "role": USER_ROLE,
                    "content": (
                        generate_response_analysis_prompt(agent_name, altered_personality, current_emotions, PERSONALITY_LANGUAGE_GUIDE, self['thoughts'][-1])
                    ),
                }

                message_queries.append(response_query)
                response_content = await get_structured_query_response(message_queries, get_message_schema())

                if not response_content:
                    raise HTTPException(status_code=500, detail="Error - process_message_lite: generating response")
                
                agent_response_message = response_content['message']
                
                '''
                # Step 9: Evaluate bot's emotional state after responding: CLEAR
                final_emotion_query = {
                    "role": USER_ROLE,
                    "content": (
                        generate_final_emotional_response_prompt(agent_name, MIN_EMOTION_VALUE, MAX_EMOTION_VALUE, True, response_content)
                    ),
                }

                inner_dialogue.append(final_emotion_query)

                final_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema_lite())

                if not final_emotion_response:
                    raise HTTPException(status_code=500, detail="Error - process_message_lite: reflecting on emotion")

                inner_dialogue.append({
                    "role": BOT_ROLE,
                    "content": json.dumps(final_emotion_response),
                })

                current_emotions = deep_merge(self["emotional_status"], final_emotion_response)
                '''
            elif response_choice["response_choice"] == IGNORE_CHOICE:
                response_content = {'message': "..."}
                agent_response_message = response_content['message']
                '''
                # Step 8-9: Evaluate bot's emotional state after ignoring the message: CLEAR
                final_emotion_query = {
                    "role": USER_ROLE,
                    "content": (
                        generate_final_emotional_response_prompt(agent_name, MIN_EMOTION_VALUE, MAX_EMOTION_VALUE, False)
                    ),
                }

                inner_dialogue.append(final_emotion_query)

                final_emotion_response = await get_structured_query_response(inner_dialogue, get_emotion_status_schema_lite())

                if not final_emotion_response:
                    raise HTTPException(status_code=500, detail="Error - process_message_lite: reflecting on emotion")

                inner_dialogue.append({
                    "role": BOT_ROLE,
                    "content": json.dumps(final_emotion_response),
                })

                current_emotions = deep_merge(self["emotional_status"], final_emotion_response)
                '''

            # Return the response to the user
            messageResponse = MessageResponse(response=agent_response_message)
            
            asyncio.create_task(
                process_remaining_steps(
                agent_name, username, db, user, self, conversation, altered_personality, 
                current_emotions, message_analysis, response_choice, response_content, received_date, message_queries, user_lite_collection
                )
            )
            
            return messageResponse
            
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
                      
async def process_remaining_steps(agent_name, username, db, user, self, conversation, altered_personality, 
                current_emotions, message_analysis, response_choice, response_content, received_date, message_queries, user_lite_collection):
    # Step 10: Sentiment Reflection: CLEAR
    sentiment_query = {
                "role": USER_ROLE,
                "content": (
                    generate_sentiment_analysis_prompt(agent_name, username, MIN_SENTIMENT_VALUE, MAX_SENTIMENT_VALUE)
                ),
            }
    message_queries.append(sentiment_query)
    
    sentiment_response = await get_structured_query_response(message_queries, get_sentiment_status_schema_lite())

    if not sentiment_response:
        raise HTTPException(status_code=500, detail="Error - process_message_lite: reflecting on sentiment")
    
    message_queries.append({
                "role": BOT_ROLE,
                "content": json.dumps(sentiment_response),
            })
            
    current_sentiments = deep_merge(user["sentiment_status"], sentiment_response)

    #Step 11:  Summary Reflection: CLEAR
    summary_query = {
                "role": USER_ROLE,
                "content": (
                    generate_summary_update_prompt(agent_name, username, user['summary'] )
                ),
            }
            
    message_queries.append(summary_query)

    summary_response = await get_structured_query_response(message_queries, get_summary_schema())

    if not summary_response:
        raise HTTPException(status_code=500, detail="Error - process_message_lite: reflecting on summary")

    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(summary_response),
    })
    
    #Step 12: Extrinsic Relationship Reflection: CLEAR
    extrinsic_relationship_query = {
        "role": USER_ROLE,
        "content": (
            generate_extrinsic_relationship_prompt(username, EXTRINSIC_RELATIONSHIPS)
        ),
    }

    message_queries.append(extrinsic_relationship_query)

    extrinsic_relationship_response = await get_structured_query_response(message_queries, get_extrinsic_relationship_schema())

    if not extrinsic_relationship_response:
        raise HTTPException(status_code=500, detail="Error - process_message_lite: reflecting on extrinsic relationship")

    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(extrinsic_relationship_response),
    })

    #Step 13: Self-Identity Reflection: CLEAR
    identity_query = {
        "role": USER_ROLE,
        "content": (
            generate_identity_update_prompt(agent_name, self['identity'])
        ),
    }

    message_queries.append(identity_query)

    identity_response = await get_structured_query_response(message_queries, get_identity_schema())

    if not identity_response:
        raise HTTPException(status_code=500, detail="Error - process_message_lite: reflecting on self-identity")
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(identity_response)
    })
    
    # Check if exchange altered current thought
    
    # Update and Save Conversation
    incoming_message = {
        "message": message_analysis["message"],
        "purpose": message_analysis["purpose"],
        "tone": message_analysis["tone"],
        "timestamp": datetime.now(),
        "sender": username,
        "from_agent": False
    }

    conversation["messages"].append(incoming_message)


    if response_choice["response_choice"] == RESPOND_CHOICE:
        bot_response_message = {
            "message": response_content["message"],
            "purpose": response_content["purpose"],
            "tone": response_content["tone"],
            "timestamp": datetime.now(),
            "sender": agent_name,
            "from_agent": True
        }
    
        conversation["messages"].append(bot_response_message)
        
        # Add to message collection
        new_message_response = {
        "message": response_content["message"],
        "sender": agent_name,
        "timestamp": datetime.now()
        }

        await insert_message_to_memory(agent_name, new_message_response)

    
    
    db[AGENT_LITE_COLLECTION].update_one({AGENT_NAME_PROPERTY: agent_name}, { "$set": {"identity": identity_response["identity"], "emotional_status": current_emotions }})
    db[CONVERSATION_COLLECTION].update_one({USER_NAME_PROPERTY: username, "agent_name": agent_name}, { "$set": {"messages": conversation["messages"] }})
    user_lite_collection.update_one({USER_NAME_PROPERTY: username}, { "$set": {"summary": summary_response["summary"], "sentiment_status": current_sentiments, "extrinsic_relationship": extrinsic_relationship_response["extrinsic_relationship"], "last_interaction": datetime.now() }}, bypass_document_validation=True)
            
async def alter_personality(self, user, lite_mode):
    """
    Alters the bot's personality based on the user's sentiment status and their extrinsic relationship.

    :param self: The self (bot) object
    :param user: The user object
    :param extrinsic_relationship_string: String describing the extrinsic relationship
    :param lite_mode: Boolean of lite mode
    :return: New personality object
    """
    personality = self["personality"]
    sentiment = user["sentiment_status"]
    extrinsic_relationship = user['extrinsic_relationship']
    alter_query = [
        {
        "role": "user",
        "content": (
            generate_personality_adjustment_prompt(agent_name, personality, sentiment, user[USER_NAME_PROPERTY], extrinsic_relationship, 
                                           MIN_PERSONALITY_VALUE, MAX_PERSONALITY_VALUE, 15)
            ),
        }
    ]    
    if (lite_mode):
        alter_query_response = await get_structured_query_response(alter_query, get_personality_status_schema_lite())
    else:
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
        if isinstance(value, dict):
            # If the value is a dictionary and exists in the target, recurse
            if key in target and isinstance(target[key], dict):
                target[key] = deep_merge(target[key], value, average)
            else:
                # Otherwise, directly set the value
                target[key] = value
        else:
            # Handle averaging or direct overwrite for non-dict values
            if average and key in target and isinstance(target[key], (int, float)) and isinstance(value, (int, float)):
                target[key] = (target[key] + value) / 2
            else:
                target[key] = value
    return target

async def generate_thought():
    """
    Generates a thought that the agent is having, and inputs it in the database
    """
    db = get_database()

    # Step 1: Fetch self object
    recent_all_messages = await get_message_memory(agent_name, MESSAGE_HISTORY_COUNT)
    self = await grab_self(agent_name, True)
    
    inner_dialogue = [SYSTEM_MESSAGE]
    inner_dialogue.append({
        "role": USER_ROLE,
        "content": (
            generate_thought_prompt(self, recent_all_messages)
        )
    })
    
    current_thought = await get_structured_query_response(inner_dialogue, get_thought_schema())
    
    current_thought_object = {
        "thought": current_thought['thought'],
        "timestamp": datetime.now()
    }
    
    self['thoughts'].append(current_thought_object)
    db[AGENT_LITE_COLLECTION].update_one({AGENT_NAME_PROPERTY: agent_name}, { "$set": {"thoughts": self['thoughts']}})
    
async def periodic_thinking():
    """
    Starts the thinking process, for the assigned duration
    """
    while True:
        await generate_thought()
        await asyncio.sleep(THINKING_RATE)