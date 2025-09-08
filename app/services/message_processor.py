import time
import json

from fastapi import HTTPException
from typing import Any
from datetime import datetime
from app.constants.schemas import get_message_perception_schema, get_message_schema, get_response_choice_schema, get_response_schema, get_thought_schema, implicitly_addressed_schema, update_summary_identity_relationship_schema
from app.constants.schemas_lite import get_emotion_delta_schema_lite, get_memory_schema_lite, get_personality_delta_schema_lite, get_sentiment_delta_schema_lite
from app.domain.memory import Memory
from app.domain.models import InternalMessageRequest, MessageResponse
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState, PersonalityDelta, PersonalityMatrix, SentimentDelta, SentimentMatrix
from app.services.expressions import get_available_expressions
from app.services.memory import normalize_emotional_impact_fill_zeros
from app.services.openai import get_structured_response
from app.constants.constants import BOT_ROLE, DM_TYPE, EXTRINSIC_RELATIONSHIPS, IGNORE_CHOICE, PERSONALITY_LANGUAGE_GUIDE, RESPOND_CHOICE, SYSTEM_MESSAGE, USER_ROLE
from app.core.config import AGENT_NAME, MESSAGE_HISTORY_COUNT, CONVERSATION_MESSAGE_RETENTION_COUNT
from app.services.database import add_memory, add_thought, get_all_message_memory, get_thoughts, grab_user, grab_self, get_conversation, insert_message_to_conversation, insert_message_to_message_memory, update_agent_emotions, update_summary_identity_relationship, update_tags, update_user_sentiment
from app.services.prompting import build_emotion_delta_prompt, build_implicit_addressing_prompt, build_memory_prompt, build_message_perception_prompt, build_message_thought_prompt, build_personality_delta_prompt, build_post_response_processing_prompt, build_response_analysis_prompt, build_response_choice_prompt, build_response_prompt, build_sentiment_delta_prompt
from app.services.state_reducer import apply_deltas_emotion, apply_deltas_personality, apply_deltas_sentiment


async def process_message(request: InternalMessageRequest):
        """
        Process a user message and return the bot's response.

        :param request: Request containing user_id and message content
        :return: JSON response with the bot's reply
        """
        try:
            timings = {}
            start = time.perf_counter()
            
            received_date = datetime.now() 
            self = await grab_self()
            user = await grab_user(request.user_id)
            conversation = await get_conversation(request.user_id)
            recent_all_messages = await get_all_message_memory(MESSAGE_HISTORY_COUNT)
            recent_user_messages = conversation["messages"][-CONVERSATION_MESSAGE_RETENTION_COUNT:] if "messages" in conversation else []
            
            timings["message_handling_setup"] = time.perf_counter() - start
            step_start = time.perf_counter()
            
            response = await handle_message(
                        self,
                        user,
                        recent_user_messages,
                        recent_all_messages,
                        received_date,
                        request,
                        direct_message=request.type == DM_TYPE
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
    request: InternalMessageRequest,
    direct_message: bool = True,
) -> MessageResponse: 
    user_id = user["user_id"]
    username = user['username']
    implicitly_addressed = True
    timings = {}
    start = time.perf_counter()
    latest_thoughts = await get_thoughts(1)
    
    # ---- -1) Group Message: Check if Implicity Addressed -------------------------------------------   
    if not direct_message:
        prompt = build_implicit_addressing_prompt(
            message_memory=recent_all_messages, 
            new_message=request.message, 
            sender_id=user_id, 
            sender_username=username
        )
        implicit_addressing_result = await get_structured_response([{"role": USER_ROLE, "content": prompt}], implicitly_addressed_schema())
        
        implicitly_addressed = implicit_addressing_result["implicitly_addressed"] == 'yes'
        
        timings["implicit_check"] = time.perf_counter() - start
        step_start = time.perf_counter()
    
    # ---- 0) Customize Personality ------------------------------------------- 
    
       
    prompt = build_personality_delta_prompt(
        agent=self,
        user=user,
        recent_messages=recent_user_messages,         
        recent_all_messages=recent_all_messages,
        received_date=str(received_date),
        user_message=request.message,
        latest_thought=latest_thoughts
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
        user=user,
        agent=self,
        recent_user_messages=recent_user_messages,
        recent_all_messages=recent_all_messages,
        received_date=str(received_date),
        user_message=request.message,
        latest_thought=latest_thoughts
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
        await update_agent_emotions(self["emotional_status"])
        
    current_emotions = self["emotional_status"]
    
    await update_agent_emotions(current_emotions)    
    
    timings["initial_emotion_delta"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    # ---- 2) Message Perception -------------------------------------------
    message_queries = [SYSTEM_MESSAGE, {
        "role": "user",
        "content": (
            build_message_perception_prompt(
                agent=self,
                user=user,
                recent_messages=recent_user_messages, 
                recent_all_messages=recent_all_messages, 
                user_message=request.message, 
                received_date=received_date,
                latest_thoughts=latest_thoughts
            )
        ),
    }]
    
    message_analysis = await get_structured_response(message_queries, get_message_perception_schema(), quality=False)
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(message_analysis)
        })
    
    rich_message = {
            "message": message_analysis["message"],
            "purpose": message_analysis["purpose"],
            "tone": message_analysis["tone"],
            "timestamp": received_date,
            "sender_id": user_id,
            "sender_username": username,
            "from_agent": False
        }
    
    await insert_message_to_conversation(
        user_id, 
        rich_message
    )
    
    await insert_message_to_message_memory(rich_message)
    
    if message_analysis["thought"] != "no":
        await add_thought(
        {
            "thought": message_analysis["thought"],
            "timestamp": datetime.now()
        } 
    )
    
    timings["message_analysis"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    # ---- 3) Response -------------------------------------------
    memory = []
    
    message_queries.append({
        "role": "user",
        "content": (
            build_response_prompt(
                user_id=user_id,
                username=username,
                personality=altered_personality, 
                current_emotions=current_emotions, 
                personality_language_guide=PERSONALITY_LANGUAGE_GUIDE, 
                latest_thought=latest_thoughts, 
                recent_messages=recent_user_messages, 
                recent_all_messages=recent_all_messages, 
                memory=memory, 
                expressions=get_available_expressions(),
                implicit=implicitly_addressed)
        ),
    })
    
    response = await get_structured_response(message_queries, get_response_schema())
    
    message_queries.append({
        "role": BOT_ROLE,
        "content": json.dumps(response)
    })
    
    selected_expression = response["response"]['expression']
    
    if response["response_choice"] == RESPOND_CHOICE:
        agent_response_message = response["response"]['message']
        rich_message = {
                "message": response["response"]["message"],
                "purpose": response["response"]["purpose"],
                "tone": response["response"]["tone"],
                "timestamp": datetime.now(),
                "sender_id": AGENT_NAME,
                "sender_username": AGENT_NAME,
                "from_agent": True
            }
        
        await insert_message_to_conversation(
            user_id, 
            rich_message
        )
        
        await insert_message_to_message_memory(rich_message)
        # Could add emotional another delta
    else:
        agent_response_message = None
        # Could add emotional another delta

    timings["response"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
        
    # ---- 4) Sentiment reflection -------------------------------------------
    message_queries.append({
                "role": USER_ROLE,
                "content": (
                    build_sentiment_delta_prompt(user)
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
    
    await update_user_sentiment(user_id, user["sentiment_status"])
    
    timings["sentiments"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    # ---- 6) Post-response processing (summary/identity/relationships) ------
    message_queries.append({
        "role": USER_ROLE,
        "content": (build_post_response_processing_prompt(
            current_identity=self["identity"], 
            user_id=user_id, 
            extrinsic_relationship_options=EXTRINSIC_RELATIONSHIPS, 
            current_summary=user["summary"]
            ))
    })
    
    post_response_processing_response = await get_structured_response(message_queries, update_summary_identity_relationship_schema(), False)
    
    await update_summary_identity_relationship(user_id, post_response_processing_response['summary'], post_response_processing_response['extrinsic_relationship'], post_response_processing_response['identity'])

    message_queries.append({"role": BOT_ROLE, "content": json.dumps(post_response_processing_response)})
    
    timings["post_response_processing"] = time.perf_counter() - step_start
    step_start = time.perf_counter()
    
    # ---- 5) Create memory ----------------------------------------------
    message_queries.append({
            "role": USER_ROLE, 
            "content": build_memory_prompt(self['memory_tags'])
        })
        
    memory_response = await get_structured_response(message_queries, get_memory_schema_lite(), quality=False)
    
    if memory_response and memory_response.get("event") and memory_response.get("thoughts"):
        mem = Memory(
            agent_name=AGENT_NAME,
            user_id=user_id,
            event=memory_response["event"],
            thoughts=memory_response["thoughts"],
            significance=memory_response.get("significance", "low"),
            emotional_impact=normalize_emotional_impact_fill_zeros(memory_response.get("emotional_impact")),
            tags=[t for t in (memory_response.get("tags") or []) if t][:3],
        )
        
        await add_memory(mem)
        await update_tags(memory_response.get("tags") or [])
    
        timings["memory_creation"] = time.perf_counter() - step_start
        
    message_queries.append({"role": BOT_ROLE, "content": json.dumps(memory_response)})
        
    # ---- 6) Update thought ----------------------------------------------
    previous_thought = await get_thoughts(1)
    
    thought_prompt = {
        "role": USER_ROLE,
        "content": (
            build_message_thought_prompt(self, previous_thought)
        )
    }
    
    message_queries.append(thought_prompt)
    
    current_thought = await get_structured_response(message_queries, get_thought_schema())
    
    if current_thought["thought"] == "no":
        return
    
    await add_thought(
        {
            "thought": current_thought['thought'],
            "timestamp": datetime.now()
        } 
    )
           
    # ---- 7) Return response ----------------------------------------------
   
    timings["total_message_handling"] = time.perf_counter() - start
    
    print("\nStep timings (seconds):")
    for step, duration in timings.items():
        print(f"{step}: {duration:.4f}")
    
    return MessageResponse(response=agent_response_message, time=int(round(timings["total_message_handling"])), expression=selected_expression)