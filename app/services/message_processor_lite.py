import asyncio
import os
import random
import time
from fastapi import HTTPException
from typing import Dict, Any, List, Mapping, Optional
from typing import Dict, Any
from datetime import datetime

from rq import get_current_job
from app.constants.schemas import get_message_perception_schema, get_message_schema, get_personality_status_schema, get_response_choice_schema, implicitly_addressed_schema, is_memory_schema, update_summary_identity_relationship_schema
from app.constants.schemas_lite import get_emotion_status_schema_lite, get_personality_status_schema_lite, get_sentiment_status_schema_lite
from app.domain.models import MessageRequest, MessageResponse
from app.services.openai import check_for_memory, get_structured_response
import json
from app.constants.constants import BOT_ROLE, CONVERSATION_MESSAGE_RETENTION_COUNT, EXTRINSIC_RELATIONSHIPS, GC_TYPE, IGNORE_CHOICE, MAX_EMOTION_VALUE, MAX_SENTIMENT_VALUE, MESSAGE_HISTORY_COUNT, MIN_EMOTION_VALUE, MIN_PERSONALITY_VALUE, MAX_PERSONALITY_VALUE, MIN_SENTIMENT_VALUE, PERSONALITY_LANGUAGE_GUIDE, RESPOND_CHOICE, SYSTEM_MESSAGE, USER_NAME_PROPERTY, USER_ROLE
from app.services.database import get_message_memory, grab_user, grab_self, get_conversation, get_database, insert_message_to_conversation, insert_message_to_memory, insert_agent_memory, update_agent_emotions, update_summary_identity_relationship, update_user_sentiment
from dotenv import load_dotenv
from app.services.prompting import build_implicit_addressing_prompt, build_initial_emotional_response_prompt, build_memory_worthiness_prompt, build_memory_prompt, build_message_perception_prompt, build_personality_adjustment_prompt, build_post_response_processing_prompt, build_response_analysis_prompt, build_response_choice_prompt, build_sentiment_analysis_prompt
from app.services.utility import get_random_memories
from app.tasks import _publish_progress

agent_name = os.getenv("BOT_NAME")

EXPRESSION_LIST = ["neutral", "happy", "sad", "angry", "fearful", "surprised", "disgusted", "thinking", "playful", "curious", "blushing", "love", "confident"]

load_dotenv()

async def process_message(request: MessageRequest):
        """
        Process a user message and return the bot's response.

        :param request: Request containing user_id and message content
        :return: JSON response with the bot's reply
        """
        try:
            timings = {}
            start = time.perf_counter()
            received_date = datetime.now() 
            username = request.username
            self = await grab_self(agent_name)
            user = await grab_user(username, agent_name)
            conversation = await get_conversation(username, agent_name)

            new_message_request = {
                "message": request.message,
                "sender": username,
                "timestamp": received_date
            }
            
            general_message_memory = await get_message_memory(agent_name, MESSAGE_HISTORY_COUNT)
        
            await insert_message_to_memory(agent_name, new_message_request)
            
            recent_all_messages = general_message_memory.append(new_message_request)
            
            recent_messages = conversation["messages"][-CONVERSATION_MESSAGE_RETENTION_COUNT:] if "messages" in conversation else []
            
            timings["message_handling_setup"] = time.perf_counter() - start
            step_start = time.perf_counter()

            if (request.type == GC_TYPE):
                response = await group_message(
                    agent_name, 
                    general_message_memory,
                    new_message_request,
                    username,
                    user,
                    recent_messages,
                    recent_all_messages,
                    received_date,
                    request,
                    self
                )
            else:
                response = await direct_message(
                    self,
                    user,
                    username,
                    recent_messages,
                    recent_all_messages,
                    received_date,
                    request
                )
                
            timings["message_handling"] = time.perf_counter() - step_start
            # Print timings
            print("\nStep timings (seconds):")
            for step, duration in timings.items():
                print(f"{step}: {duration:.4f}")
            
            return response
                
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
                               
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
            build_personality_adjustment_prompt(agent_name, personality, sentiment, user[USER_NAME_PROPERTY], extrinsic_relationship, 
                                           MIN_PERSONALITY_VALUE, MAX_PERSONALITY_VALUE, 15)
            ),
        }
    ]    
    if (lite_mode):
        alter_query_response = await get_structured_response(alter_query, get_personality_status_schema_lite(), False)
    else:
        alter_query_response = await get_structured_response(alter_query, get_personality_status_schema())

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

async def group_message(
    agent_name: str,
    general_message_memory: Any,
    new_message_request: Any,
    username: str,
    user: Any,
    recent_messages: Any,
    recent_all_messages: Any,
    received_date: datetime,
    request: Any,
    self: Any,
) -> MessageResponse:
    implicit_addressing_result = await get_structured_response([{
        "role": USER_ROLE,
        "content": (
            build_implicit_addressing_prompt(agent_name, general_message_memory, new_message_request)
        )
    }], implicitly_addressed_schema())
    
    # TODO If not implicitly addressed check if they want to respond anyway
    # TODO Identify different group chats with an identifier sent from the client, so that group chat memory can be implemented
    if (implicit_addressing_result["implicitly_addressed"] == 'no'):
        initial_emotion_query = {
            "role": "user",
            "content": (build_initial_emotional_response_prompt(agent_name, self['personality'], self['emotional_status'], username, user['summary'], user["intrinsic_relationship"], user['extrinsic_relationship'], recent_messages, recent_all_messages, received_date, request.message, MIN_EMOTION_VALUE, MAX_EMOTION_VALUE, self['thoughts'][-1])),
        }

        initial_emotion_response = await get_structured_response([SYSTEM_MESSAGE, initial_emotion_query], get_emotion_status_schema_lite())

        current_emotions = deep_merge(self["emotional_status"], initial_emotion_response)

        # Step 6: Analyze the purpose and tone of the user's message: CLEAR
        message_queries = [SYSTEM_MESSAGE, {
            "role": "user",
            "content": (
                build_message_perception_prompt(agent_name, self['personality'], current_emotions, username, user['summary'], user["intrinsic_relationship"], user['extrinsic_relationship'], recent_messages, recent_all_messages, request.message, received_date)
            ),
        }]
        
        message_analysis = await get_structured_response(message_queries, get_message_schema())
        
        message_queries.append({
            "role": BOT_ROLE,
            "content": json.dumps(message_analysis)
            })
    
        # Step 7: Determine whether to respond: CLEAR
        response_choice_query = {
            "role": "user",
            "content": (
                build_response_choice_prompt(agent_name, username, False)
            ),
        }
        
        message_queries.append(response_choice_query)

        response_choice = await get_structured_response(message_queries, get_response_choice_schema())
        
        message_queries.append({
            "role": BOT_ROLE,
            "content": json.dumps(response_choice)
            })
        
        if response_choice["response_choice"] == RESPOND_CHOICE:
            memory = get_random_memories(self)
            response_query = {
                "role": USER_ROLE,
                "content": (
                    build_response_analysis_prompt(agent_name, self['personality'], current_emotions, PERSONALITY_LANGUAGE_GUIDE, self['thoughts'][-1], username, recent_messages, recent_all_messages, memory)
                ),
            }

            message_queries.append(response_query)
            response_content = await get_structured_response(message_queries, get_message_schema())
            
            agent_response_message = response_content['message']
        elif response_choice["response_choice"] == IGNORE_CHOICE:
            response_content = None
            agent_response_message = None
            
        # ---- 0) Save Messages -------------------------------------------
        await insert_message_to_conversation(
            username, 
            agent_name, 
            {
                "message": message_analysis["message"],
                "purpose": message_analysis["purpose"],
                "tone": message_analysis["tone"],
                "timestamp": received_date,
                "sender": username,
                "from_agent": False
            }
        )
        
        print(response_choice)
        if response_choice["response_choice"] == RESPOND_CHOICE:
            await insert_message_to_conversation(
                username, 
                agent_name, 
                {
                    "message": response_content["message"],
                    "purpose": response_content["purpose"],
                    "tone": response_content["tone"],
                    "timestamp": datetime.now(),
                    "sender": agent_name,
                    "from_agent": True
                }
            )
            
            await insert_message_to_memory(
                agent_name, 
                {
                "message": response_content["message"],
                "sender": agent_name,
                "timestamp": datetime.now()
                }
            )
        
        # ---- 1) Sentiment reflection -------------------------------------------
        message_queries.append({
                    "role": USER_ROLE,
                    "content": (
                        build_sentiment_analysis_prompt(agent_name, username, MIN_SENTIMENT_VALUE, MAX_SENTIMENT_VALUE)
                    ),
                })
        
        sentiment_response = await get_structured_response(message_queries, get_sentiment_status_schema_lite())

        if not sentiment_response:
            raise HTTPException(status_code=500, detail="Error - process_message_lite: reflecting on sentiment")
        
        message_queries.append({
                    "role": BOT_ROLE,
                    "content": json.dumps(sentiment_response),
                })
                
        current_sentiments = deep_merge(user["sentiment_status"], sentiment_response)
        
        # ---- 2) Post-response processing (summary/identity/relationships) ------
        message_queries.append({
            "role": USER_ROLE,
            "content": (build_post_response_processing_prompt(agent_name, self["identity"], username, EXTRINSIC_RELATIONSHIPS, user["summary"]))
        })
        
        post_response_processing_response = await get_structured_response(message_queries, update_summary_identity_relationship_schema())
        
        await update_summary_identity_relationship(agent_name, username, post_response_processing_response['summary'], post_response_processing_response['extrinsic_relationship'], post_response_processing_response['identity'])

        message_queries.append({"role": BOT_ROLE, "content": json.dumps(post_response_processing_response)})
        
        # ---- 3) Memory worthiness ----------------------------------------------
        message_queries.append({
            "role": USER_ROLE,
            "content": (build_memory_worthiness_prompt(agent_name))
        })
        
        is_memory_response = await get_structured_response(message_queries, is_memory_schema())
        
        if not is_memory_response:
            raise HTTPException(status_code=500, detail="Error - process_message_lite: determining if memory will be extracted")
        
        message_queries.append({
            "role": BOT_ROLE,
            "content": json.dumps(is_memory_response)
        })
        
        if (is_memory_response["is_memory"] == "yes"):
            message_queries.append({
                "role": USER_ROLE, 
                "content": build_memory_prompt(agent_name, self['memory_profile']['all_tags'])
            })
            check_for_memory_response = await check_for_memory(message_queries)
            function = eval(check_for_memory_response.function_call.name)
            params = json.loads(check_for_memory_response.function_call.arguments)
            await function(**params)
        
        await update_agent_emotions(agent_name, current_emotions)
        
        await update_user_sentiment(username, current_sentiments)
                        
        return MessageResponse(response=agent_response_message) 
    
async def direct_message(
    self: Any,
    user: Any,
    username: str,
    recent_messages: Any,
    recent_all_messages: Any,
    received_date: datetime,
    request: Any,
) -> MessageResponse:
    job = get_current_job()
    # --- progress 0% ---
    job.meta["progress"] = 5
    job.save_meta()
    _publish_progress(job.id, 5)
    
    timings = {}
    start = time.perf_counter()
    altered_personality = await alter_personality(self, user, True)
    
    timings["alter_personality"] = time.perf_counter() - start
    step_start = time.perf_counter()
    
    # Assess emotional response upon first viewing message
    initial_emotion_query = {
        "role": "user",
        "content": (build_initial_emotional_response_prompt(agent_name, altered_personality, self['emotional_status'], username, user['summary'], user["intrinsic_relationship"], user['extrinsic_relationship'], recent_messages, recent_all_messages, received_date, request.message, MIN_EMOTION_VALUE, MAX_EMOTION_VALUE, self['thoughts'][-1])),
    }
    initial_emotion_response = await get_structured_response([SYSTEM_MESSAGE, initial_emotion_query], get_emotion_status_schema_lite(), False)
    
    timings["initial_emotion_response"] = time.perf_counter() - step_start
    step_start = time.perf_counter()

    current_emotions = deep_merge(self["emotional_status"], initial_emotion_response)
    
    message_queries = [SYSTEM_MESSAGE, {
        "role": "user",
        "content": (
            build_message_perception_prompt(agent_name, altered_personality, current_emotions, username, user['summary'], user["intrinsic_relationship"], user['extrinsic_relationship'], recent_messages, recent_all_messages, request.message, received_date)
        ),
    }]
    
    message_analysis = await get_structured_response(message_queries, get_message_perception_schema())
    
    timings["message_analysis"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(message_analysis)
        })

    # Step 7: Determine whether to respond: CLEAR
    message_queries.append({
        "role": "user",
        "content": (
            build_response_choice_prompt(agent_name, username)
        ),
    })

    response_choice = await get_structured_response(message_queries, get_response_choice_schema())
    
    timings["response_choice"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(response_choice)
        })
    
    if response_choice["response_choice"] == RESPOND_CHOICE:
        memory = get_random_memories(self)

        message_queries.append({
            "role": USER_ROLE,
            "content": (
                build_response_analysis_prompt(agent_name, altered_personality, current_emotions, PERSONALITY_LANGUAGE_GUIDE, self['thoughts'][-1], username, recent_messages, recent_all_messages, memory, EXPRESSION_LIST)
            ),
        })
        response_content = await get_structured_response(message_queries, get_message_schema())
        
        agent_response_message = response_content['message']
        selected_expression = response_content['expression']
        
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
        response_content = None
        agent_response_message = None
        selected_expression = 'neutral'
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
        
    timings["response"] = time.perf_counter() - step_start
    step_start = time.perf_counter()

    
    # ---- 0) Save Messages -------------------------------------------
    await insert_message_to_conversation(
        username, 
        agent_name, 
        {
            "message": message_analysis["message"],
            "purpose": message_analysis["purpose"],
            "tone": message_analysis["tone"],
            "timestamp": received_date,
            "sender": username,
            "from_agent": False
        }
    )
    
    if response_choice["response_choice"] == RESPOND_CHOICE:
        await insert_message_to_conversation(
            username, 
            agent_name, 
            {
                "message": response_content["message"],
                "purpose": response_content["purpose"],
                "tone": response_content["tone"],
                "timestamp": datetime.now(),
                "sender": agent_name,
                "from_agent": True
            }
        )
        
        await insert_message_to_memory(
            agent_name, 
            {
            "message": response_content["message"],
            "sender": agent_name,
            "timestamp": datetime.now()
            }
        )
    
    # ---- 1) Sentiment reflection -------------------------------------------
    message_queries.append({
                "role": USER_ROLE,
                "content": (
                    build_sentiment_analysis_prompt(agent_name, username, MIN_SENTIMENT_VALUE, MAX_SENTIMENT_VALUE)
                ),
            })
    
    sentiment_response = await get_structured_response(message_queries, get_sentiment_status_schema_lite(), False)
    
    timings["sentiments"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    message_queries.append({
                "role": BOT_ROLE,
                "content": json.dumps(sentiment_response),
            })
            
    current_sentiments = deep_merge(user["sentiment_status"], sentiment_response)
    
    # ---- 2) Post-response processing (summary/identity/relationships) ------
    message_queries.append({
        "role": USER_ROLE,
        "content": (build_post_response_processing_prompt(agent_name, self["identity"], username, EXTRINSIC_RELATIONSHIPS, user["summary"]))
    })
    
    post_response_processing_response = await get_structured_response(message_queries, update_summary_identity_relationship_schema())
    
    timings["post_response_processing"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    await update_summary_identity_relationship(agent_name, username, post_response_processing_response['summary'], post_response_processing_response['extrinsic_relationship'], post_response_processing_response['identity'])

    message_queries.append({"role": BOT_ROLE, "content": json.dumps(post_response_processing_response)})
    
    # ---- 3) Memory worthiness ----------------------------------------------
    message_queries.append({
        "role": USER_ROLE,
        "content": (build_memory_worthiness_prompt(agent_name))
    })
    
    is_memory_response = await get_structured_response(message_queries, is_memory_schema())
    
    timings["memory_worthiness"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(is_memory_response)
    })
    
    if (is_memory_response["is_memory"] == "yes"):
        message_queries.append({
            "role": USER_ROLE, 
            "content": build_memory_prompt(agent_name, self['memory_profile']['all_tags'])
        })
        check_for_memory_response = await check_for_memory(message_queries)
        function = eval(check_for_memory_response.function_call.name)
        params = json.loads(check_for_memory_response.function_call.arguments)
        await function(**params)
    
    await update_agent_emotions(agent_name, current_emotions)
    
    await update_user_sentiment(username, current_sentiments)
    
    timings["total_message_handling"] = time.perf_counter() - start
    
    print("\nStep timings (seconds):")
    for step, duration in timings.items():
        print(f"{step}: {duration:.4f}")
    
    return MessageResponse(response=agent_response_message, time=int(round(timings["total_message_handling"])), expression=selected_expression)