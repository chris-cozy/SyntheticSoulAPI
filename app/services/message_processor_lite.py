import time
import json

from fastapi import HTTPException
from typing import Any
from datetime import datetime
from app.constants.schemas import get_message_perception_schema, get_message_schema, get_response_choice_schema, implicitly_addressed_schema, update_summary_identity_relationship_schema
from app.constants.schemas_lite import get_emotion_delta_schema_lite, get_memory_schema_lite, get_personality_delta_schema_lite, get_sentiment_delta_schema_lite
from app.domain.memory import Memory
from app.domain.models import MessageRequest, MessageResponse
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState, PersonalityDelta, PersonalityMatrix, SentimentDelta, SentimentMatrix
from app.services.memory import normalize_emotional_impact_fill_zeros
from app.services.openai import get_structured_response
from app.constants.constants import AGENT_NAME, BOT_ROLE, CONVERSATION_MESSAGE_RETENTION_COUNT, EXPRESSION_LIST, EXTRINSIC_RELATIONSHIPS, GC_TYPE, IGNORE_CHOICE, MESSAGE_HISTORY_COUNT, PERSONALITY_LANGUAGE_GUIDE, RESPOND_CHOICE, SYSTEM_MESSAGE, USER_NAME_PROPERTY, USER_ROLE
from app.services.database import add_memory, get_message_memory, grab_user, grab_self, get_conversation, insert_message_to_conversation, insert_message_to_memory, update_agent_emotions, update_summary_identity_relationship, update_user_sentiment
from app.services.prompting import build_emotion_delta_prompt, build_implicit_addressing_prompt, build_memory_prompt, build_message_perception_prompt, build_personality_delta_prompt, build_post_response_processing_prompt, build_response_analysis_prompt, build_response_choice_prompt, build_sentiment_delta_prompt
from app.services.state_reducer import apply_deltas_emotion, apply_deltas_personality, apply_deltas_sentiment
from app.services.utility import get_random_memories


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
            self = await grab_self(AGENT_NAME)
            user = await grab_user(username, AGENT_NAME)
            conversation = await get_conversation(username, AGENT_NAME)
                    
            await insert_message_to_memory(AGENT_NAME, {
                "message": request.message,
                "sender": username,
                "timestamp": received_date
            })
            
            recent_all_messages = await get_message_memory(AGENT_NAME, MESSAGE_HISTORY_COUNT)
            
            recent_user_messages = conversation["messages"][-CONVERSATION_MESSAGE_RETENTION_COUNT:] if "messages" in conversation else []
            
            timings["message_handling_setup"] = time.perf_counter() - start
            step_start = time.perf_counter()

            if (request.type == GC_TYPE):
                response = await handle_message(
                    self,
                    user,
                    recent_user_messages,
                    recent_all_messages,
                    received_date,
                    request,
                    False
                )
            else:
                response = await handle_message(
                    self,
                    user,
                    recent_user_messages,
                    recent_all_messages,
                    received_date,
                    request
                )
                
            timings["message_handling_completion"] = time.perf_counter() - step_start
            # Print timings
            print("\nStep timings (seconds):")
            for step, duration in timings.items():
                print(f"{step}: {duration:.4f}")
            
            return response
                
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
                               

async def handle_message(
    self: Any,
    user: Any,
    recent_user_messages: Any,
    recent_all_messages: Any,
    received_date: datetime,
    request: Any,
    direct_message: bool = True,
) -> MessageResponse: 
    username = user['username']
    implicitly_addressed = True
    timings = {}
    start = time.perf_counter()
    
    # ---- -1) Group Message: Check if Implicity Addressed -------------------------------------------   
    if not direct_message:
        prompt = build_implicit_addressing_prompt(AGENT_NAME, recent_all_messages, request)
        implicit_addressing_result = await get_structured_response([{"role": USER_ROLE, "content": prompt}], implicitly_addressed_schema())
        
        implicitly_addressed = implicit_addressing_result["implicitly_addressed"] == 'yes'
        
        timings["implicit_check"] = time.perf_counter() - start
        step_start = time.perf_counter()
    
    # ---- 0) Customize Personality -------------------------------------------    
    prompt = build_personality_delta_prompt(
        AGENT_NAME,
        personality=self["personality"],
        sentiment_status=user["sentiment_status"],
        user_name=user[USER_NAME_PROPERTY],
        extrinsic_relationship=user['extrinsic_relationship'],
        recent_messages=recent_user_messages,         
        recent_all_messages=recent_all_messages,
        received_date=str(received_date),
        user_message=request.message,
        latest_thought=self['thoughts'][-1] or ""
    )
    
    delta = await get_structured_response([{"role": "user", "content": prompt}], get_personality_delta_schema_lite(), False)
            
    if delta and delta.get("deltas"):
        # Convert existing DB personality_matrix -> PersonalityMatrix
        flat = self["personality"].get("personality_matrix", {})
        mat = PersonalityMatrix(traits={k: BoundedTrait(**v) for k, v in flat.items()})
        
        # Apply
        new_mat = apply_deltas_personality(
            mat, PersonalityDelta(**delta), cap=3.0  # personality changes are slower
        )
        
        # Put back into the persisted shape
        self["personality"]["personality_matrix"] = {
            k: new_mat.traits[k].model_dump() if k in new_mat.traits else v
            for k, v in flat.items()
        }
    
    altered_personality = self["personality"]
    
    timings["personality_delta"] = time.perf_counter() - start
    step_start = time.perf_counter()
    
    # ---- 1) Initial Emotional Reaction -------------------------------------------
    prompt = build_emotion_delta_prompt(
        AGENT_NAME,
        altered_personality,
        emotional_status=self["emotional_status"],        # current values
        user_name=user[USER_NAME_PROPERTY],
        user_summary=user.get("summary", ""),
        intrinsic_relationship=user.get("intrinsic_relationship", ""),
        extrinsic_relationship=user.get("extrinsic_relationship", ""),
        recent_user_messages=recent_user_messages,
        recent_all_messages=recent_all_messages,
        received_date=str(received_date),
        user_message=request.message,
        latest_thought=self['thoughts'][-1] or ""
    )
    
    delta = await get_structured_response(
        [{"role": "user", "content": prompt}],
        get_emotion_delta_schema_lite(),
        quality=False
    )
    if delta and delta.get("deltas"):  # only apply if anything changed
        current = self["emotional_status"]
        emo = EmotionalState(
            emotions={k: BoundedTrait(**v) for k, v in current["emotions"].items()},
            reason=current.get("reason")
        )
        new_state = apply_deltas_emotion(emo, EmotionalDelta(**delta), cap=7.0)
        # persist back in your DB shape
        self["emotional_status"]["emotions"] = {
            k: new_state.emotions[k].model_dump() for k in new_state.emotions
        }
        if new_state.reason:
            self["emotional_status"]["reason"] = new_state.reason
        # save with your existing DB function
        await update_agent_emotions(self["name"], self["emotional_status"])
        
    current_emotions = self["emotional_status"]    
    
    timings["initial_emotion_delta"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    # ---- 2) Message Perception -------------------------------------------
    message_queries = [SYSTEM_MESSAGE, {
        "role": "user",
        "content": (
            build_message_perception_prompt(AGENT_NAME, altered_personality, current_emotions, username, user['summary'], user["intrinsic_relationship"], user['extrinsic_relationship'], recent_user_messages, recent_all_messages, request.message, received_date)
        ),
    }]
    
    message_analysis = await get_structured_response(message_queries, get_message_perception_schema(), quality=False)
    
    timings["message_analysis"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(message_analysis)
        })

    # ---- 3) Decide If Respond -------------------------------------------
    message_queries.append({
        "role": "user",
        "content": (
            build_response_choice_prompt(AGENT_NAME, username, implicit=implicitly_addressed)
        ),
    })

    response_choice = await get_structured_response(message_queries, get_response_choice_schema(), False)
    
    timings["response_choice"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(response_choice)
        })
    
    # ---- 4) Respond -------------------------------------------
    if response_choice["response_choice"] == RESPOND_CHOICE:
        memory = get_random_memories(self)

        message_queries.append({
            "role": USER_ROLE,
            "content": (
                build_response_analysis_prompt(AGENT_NAME, altered_personality, current_emotions, PERSONALITY_LANGUAGE_GUIDE, self['thoughts'][-1], username, recent_user_messages, recent_all_messages, memory, EXPRESSION_LIST)
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

    
    # ---- 5) Save Messages -------------------------------------------
    await insert_message_to_conversation(
        username, 
        AGENT_NAME, 
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
            AGENT_NAME, 
            {
                "message": response_content["message"],
                "purpose": response_content["purpose"],
                "tone": response_content["tone"],
                "timestamp": datetime.now(),
                "sender": AGENT_NAME,
                "from_agent": True
            }
        )
        
        await insert_message_to_memory(
            AGENT_NAME, 
            {
            "message": response_content["message"],
            "sender": AGENT_NAME,
            "timestamp": datetime.now()
            }
        )
    
    # ---- 6) Sentiment reflection -------------------------------------------
    message_queries.append({
                "role": USER_ROLE,
                "content": (
                    build_sentiment_delta_prompt(AGENT_NAME, username, user["sentiment_status"])
                ),
            })
    
    delta = await get_structured_response(message_queries, get_sentiment_delta_schema_lite(), False)
            
    if delta and delta.get("deltas"):
        # Convert existing DB sentiment_status -> SentimentMatrix
        flat = user["sentiment_status"]
        mat = SentimentMatrix(
            sentiments={k: BoundedTrait(**v) for k, v in flat["sentiments"].items()},
            reason=flat.get("reason")
        )
                
        # Apply
        new_mat = apply_deltas_sentiment(
            mat, SentimentDelta(**delta), cap=5.0  # sentiment changes are slower
        )
        
        # Put back into the persisted shape        
        user["sentiment_status"]["sentiments"] = {
            k: new_mat.sentiments[k].model_dump() for k in new_mat.sentiments
        }
        if new_mat.reason:
            user["sentiment_status"]["reason"] = new_mat.reason
    
    current_sentiments = user["sentiment_status"]
    
    timings["sentiments"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    # ---- 7) Post-response processing (summary/identity/relationships) ------
    message_queries.append({
        "role": USER_ROLE,
        "content": (build_post_response_processing_prompt(AGENT_NAME, self["identity"], username, EXTRINSIC_RELATIONSHIPS, user["summary"]))
    })
    
    post_response_processing_response = await get_structured_response(message_queries, update_summary_identity_relationship_schema(), False)
    
    await update_summary_identity_relationship(AGENT_NAME, username, post_response_processing_response['summary'], post_response_processing_response['extrinsic_relationship'], post_response_processing_response['identity'])

    message_queries.append({"role": BOT_ROLE, "content": json.dumps(post_response_processing_response)})
    
    timings["post_response_processing"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    # ---- 8) Create memory ----------------------------------------------
    message_queries.append({
            "role": USER_ROLE, 
            "content": build_memory_prompt(AGENT_NAME, self['memory_profile']['all_tags'])
        })
        
    memory_response = await get_structured_response(message_queries, get_memory_schema_lite(), quality=False)
    
    if memory_response and memory_response.get("event") and memory_response.get("thoughts"):
        mem = Memory(
            agent_name=AGENT_NAME,
            user=username,
            event=memory_response["event"],
            thoughts=memory_response["thoughts"],
            significance=memory_response.get("significance", "low"),
            emotional_impact=normalize_emotional_impact_fill_zeros(memory_response.get("emotional_impact")),
            tags=[t for t in (memory_response.get("tags") or []) if t][:3],
        )
        
        await add_memory(mem)
    
        timings["memory_creation"] = time.perf_counter() - step_start
        
            
    # ---- 9) Update data ----------------------------------------------
    await update_agent_emotions(AGENT_NAME, current_emotions)
    
    await update_user_sentiment(username, current_sentiments)
    
    timings["total_message_handling"] = time.perf_counter() - start
    
    print("\nStep timings (seconds):")
    for step, duration in timings.items():
        print(f"{step}: {duration:.4f}")
    
    return MessageResponse(response=agent_response_message, time=int(round(timings["total_message_handling"])), expression=selected_expression)