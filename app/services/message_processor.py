import asyncio
import time
import json

from fastapi import HTTPException
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone
from app.constants.schemas import get_message_perception_schema,get_response_schema, get_thought_schema, implicitly_addressed_schema, post_processing_schema, get_memory_schema_lite, get_personality_emotion_delta_schema_lite
from app.domain.memory import Memory
from app.domain.models import GenerateReplyTaskResponse, InternalMessageRequest, MessageResponse
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState, PersonalityDelta, PersonalityMatrix, SentimentDelta, SentimentMatrix
from app.services.expressions import get_available_expressions
from app.services.memory import get_random_memory_tag, normalize_emotional_impact_fill_zeros, retrieve_relevant_memory_from_tag
from app.services.openai import structured_query
from app.constants.constants import BOT_ROLE, DM_TYPE, EXTRINSIC_RELATIONSHIPS, IGNORE_CHOICE, PERSONALITY_LANGUAGE_GUIDE, RESPOND_CHOICE, USER_ROLE
from app.core.config import AGENT_NAME, DEBUG_MODE, MESSAGE_HISTORY_COUNT, CONVERSATION_MESSAGE_RETENTION_COUNT
from app.services.database import add_memory, add_thought, get_all_message_memory, get_thoughts, grab_user, grab_self, get_conversation, insert_message_to_conversation, insert_message_to_message_memory, update_agent_emotions, update_summary_identity_relationship, update_tags, update_user_sentiment
from app.services.prompting import _system_message, build_implicit_addressing_prompt, build_memory_prompt, build_message_perception_prompt, build_message_thought_prompt, build_personality_emotional_delta_prompt, build_post_processing_prompt, build_response_prompt
from app.services.state_reducer import apply_deltas_emotion, apply_deltas_personality, apply_deltas_sentiment

        
def _normalize_delta_payload(delta_payload: Any, allowed_keys: Set[str]) -> Dict[str, Any]:
    payload = delta_payload if isinstance(delta_payload, dict) else {}
    raw_deltas = payload.get("deltas")
    clean_deltas: Dict[str, int] = {}

    if isinstance(raw_deltas, dict):
        for key, value in raw_deltas.items():
            if key not in allowed_keys:
                continue
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                clean_deltas[key] = int(round(value))

    normalized: Dict[str, Any] = {"deltas": clean_deltas}

    reason = payload.get("reason")
    if isinstance(reason, str) and reason.strip():
        normalized["reason"] = reason.strip()

    confidence = payload.get("confidence")
    if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
        normalized["confidence"] = max(0.0, min(1.0, float(confidence)))

    return normalized


def _as_dict(payload: Any) -> Dict[str, Any]:
    return payload if isinstance(payload, dict) else {}


async def generate_response(request: InternalMessageRequest) -> GenerateReplyTaskResponse:
        """
        Process a user message and return the bot's response.

        Pipeline
        --------
        0) Setup & prefetch:
            - Concurrently fetch agent/user state, conversation, message memory, and latest thoughts.
            - Initialize timing buckets.

        1) Personality & emotion deltas:
            - Ask the model for updates to agent personality/emotional state based on context.
            - Apply deltas to get `altered_personality` and `current_emotions`.

        2) Message perception:
            - Ask the model to interpret the user's latest message (message, purpose, tone, optional thought).
            - Persist the perceived message to conversation + long-term message memory.
            - If a new thought is produced, store it.

        3) Response generation:
            - Retrieve relevant memory (by random tag) and available expressions.
            - Ask the model whether/how to respond (and which expression to use).
            - If responding, persist the agent message to conversation + message memory.

        Returns
        -------
        GenerateReplyTaskResponse
            - Includes a `MessageResponse` (response text, total elapsed ms, chosen expression),
            the `user_id`, and the LLM interaction transcript in `queries`.

        Notes
        -----
        - All timings are collected in `timings` for observability.
        - Function is defensive against missing fields and keeps DMs vs. non-DMs consistent.
        - Uses monotonic clock for timings and timezone-aware timestamps.
        """
        timings: Dict[str, float] = {}
        t0 = time.perf_counter()
        
        try:
            # ---------- 0) Setup & Prefetch ----------
            step_start = time.perf_counter()
            received_dt = datetime.now(timezone.utc)
            
            # Prefetch everything that doesn't depend on anything else
            # (I/O concurrency reduces end-to-end latency).
            
            self_task = asyncio.create_task(grab_self())
            user_task = asyncio.create_task(grab_user(request.user_id))
            convo_task = asyncio.create_task(get_conversation(request.user_id))
            all_mem_task = asyncio.create_task(get_all_message_memory(MESSAGE_HISTORY_COUNT))
            thoughts_task = asyncio.create_task(get_thoughts(1))
            
            self, user, conversation, recent_all_messages, latest_thoughts = await asyncio.gather(
                self_task, user_task, convo_task, all_mem_task, thoughts_task
            )
            
            user_id: str = user.get("user_id", request.user_id)
            username: str = user.get("username", "unknown")
            
            # Guard: conversation may be None or missing 'messages'
            convo_messages: List[Dict[str, Any]] = (conversation or {}).get("messages", [])
            recent_user_messages = convo_messages[-CONVERSATION_MESSAGE_RETENTION_COUNT:] if convo_messages else []
            
            # Non-DM messages may require an implicit address check;
            # default to False for DMs.
            if getattr(request, "type", None) != DM_TYPE:
                implicitly_addressed = await check_implicit_addressed(
                    user_id=user_id,
                    username=username,
                    message=request.message,
                    recent_all_messages=recent_all_messages,
                )
            else:
                implicitly_addressed = False
            
            timings["setup_prefetch"] = time.perf_counter() - step_start
            
            queries: List[Dict[str, Any]] = []
            
            # ---------- 1) Personality & Emotion Deltas ----------
            step_start = time.perf_counter()
            sys_msg = _system_message(
                personality=self["personality"],
                emotions=self["emotional_status"],
                identity=self["identity"],
            )
            prompt = {
                "role": USER_ROLE, 
                "content": (
                    build_personality_emotional_delta_prompt(
                        user=user,
                        agent=self,
                        recent_user_messages=recent_user_messages,
                        recent_all_messages=recent_all_messages,
                        received_date=str(received_dt),
                        user_message=request.message,
                        latest_thought=latest_thoughts
                    )
                )
            }
            
            response = await structured_query(
                [sys_msg, prompt],
                get_personality_emotion_delta_schema_lite(),
                quality=False
            )
            response = _as_dict(response)
            
            altered_personality = alter_personality(response.get("personality_deltas", {}), self)
            current_emotions = await alter_emotions(response.get("emotion_deltas", {}), self)
            
            timings["personality_emotion_deltas"] = time.perf_counter() - step_start
            
            # ---- 2) Message Perception -------------------------------------------
            step_start = time.perf_counter()
            queries.append(_system_message(personality=altered_personality, emotions=current_emotions, identity=self["identity"]))
            prompt = {
                "role": "user",
                "content": (
                    build_message_perception_prompt(
                        user=user,
                        recent_messages=recent_user_messages, 
                        recent_all_messages=recent_all_messages, 
                        user_message=request.message, 
                        received_date=received_dt,
                        latest_thoughts=latest_thoughts
                    )
                ),
            }
            
            perception = await structured_query(
                queries + [prompt], 
                get_message_perception_schema(), 
                quality=False
            )
            perception = _as_dict(perception)
            
            queries.append({
                "role": BOT_ROLE,
                "content": f"This is {AGENT_NAME}'s interpretation of the latest message from {user_id}, and if it altered their current thought: {json.dumps(perception)}"
                })
            
            rich_message = {
                "message": perception.get("message", request.message),
                "purpose": perception.get("purpose"),
                "tone": perception.get("tone"),
                "timestamp": received_dt,
                "sender_id": user_id,
                "sender_username": username,
                "from_agent": False
            }
            
            # Fire-and-forget persistence can be awaited together
            persist_user_msg_task = asyncio.create_task(
                insert_message_to_conversation(user_id, rich_message)
            )
            persist_user_mem_task = asyncio.create_task(
                insert_message_to_message_memory(rich_message)
            )
            
            thought_text = perception.get("thought")
            if thought_text and str(thought_text).lower() != "no":
                add_thought_task = asyncio.create_task(add_thought({
                    "thought": thought_text,
                    "timestamp": datetime.now(timezone.utc),
                }))
            else:
                add_thought_task = None
                
            # Await persistence tasks
            await asyncio.gather(
                persist_user_msg_task,
                persist_user_mem_task,
                *( [add_thought_task] if add_thought_task else [] )
            )
            
            timings["message_perception"] = time.perf_counter() - step_start
            
            # ---- 3) Response -------------------------------------------
            step_start = time.perf_counter()
            
             # Retrieve memory + expressions concurrently
            memory_tag = get_random_memory_tag(self)
            
            retrieved_memory = await retrieve_relevant_memory_from_tag(memory_tag)
            available_expressions = get_available_expressions()
            
            memory: List[Dict[str, Any]] = retrieved_memory or []
            
            prompt = {
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
                        expressions=available_expressions,
                        implicit=implicitly_addressed,
                        message=rich_message
                    )
                ),
            }
            
            response_decision  = await structured_query(queries + [prompt], get_response_schema())
            invalid_response_decision = not isinstance(response_decision, dict)
            if not isinstance(response_decision, dict):
                response_decision = {
                    "response_choice": IGNORE_CHOICE,
                    "reason": "invalid_response_payload",
                    "response": {},
                    "expression": "neutral",
                }
            
            queries.append({
                "role": BOT_ROLE,
                "content": f"This is {AGENT_NAME}'s decision of whether to respond, and their response if any: {json.dumps(response_decision )}"
            })
            
            selected_expression = str(response_decision.get("expression") or "neutral")
            
            agent_response_message: Optional[str] = None
            response_obj = response_decision.get("response") or {}
            response_choice = str(response_decision.get("response_choice") or "").strip().lower()
            response_text = str(response_obj.get("message") or "").strip()

            # Defensive normalization: if choice is malformed but response text exists, treat it as "respond".
            if response_choice not in {RESPOND_CHOICE, IGNORE_CHOICE}:
                invalid_response_decision = True
                response_choice = RESPOND_CHOICE if response_text else IGNORE_CHOICE

            if response_choice == RESPOND_CHOICE and response_text:
                agent_response_message = response_text
                
                rich_message = {
                    "message": response_text,
                    "purpose": str(response_obj.get("purpose") or "unspecified"),
                    "tone": str(response_obj.get("tone") or "neutral"),
                    "timestamp": datetime.now(timezone.utc),
                    "sender_id": AGENT_NAME,
                    "sender_username": AGENT_NAME,
                    "from_agent": True
                }
                
                await asyncio.gather(
                    insert_message_to_conversation(user_id, rich_message),
                    insert_message_to_message_memory(rich_message),
                )

            # DM-safe fallback: if decision payload was invalid and no reply text was produced,
            # return a short deterministic response so clients do not surface a transport-level error string.
            if (
                agent_response_message is None
                and invalid_response_decision
                and getattr(request, "type", None) == DM_TYPE
            ):
                agent_response_message = "I hit a thinking issue on my side, but I should be good now. Could you resend that once?"
                fallback_message = {
                    "message": agent_response_message,
                    "purpose": "recover_from_generation_error",
                    "tone": "apologetic",
                    "timestamp": datetime.now(timezone.utc),
                    "sender_id": AGENT_NAME,
                    "sender_username": AGENT_NAME,
                    "from_agent": True,
                }
                await asyncio.gather(
                    insert_message_to_conversation(user_id, fallback_message),
                    insert_message_to_message_memory(fallback_message),
                )
                
            # Could add post response emotional delta

            timings["response_generation"] = time.perf_counter() - step_start
            
            # ---------- Finalize ----------
            total_s = time.perf_counter() - t0
            timings["total_response_generation"] = total_s
            
            if DEBUG_MODE:
                print("\nStep timings (seconds):")
                for step, duration in timings.items():
                    print(f"{step}: {duration:.4f}")
                    
                print("\nGenerate Response Query List")
                print(queries)

            message_response = MessageResponse(
                response=agent_response_message,
                time=int(total_s),
                expression=selected_expression,
            )

            return GenerateReplyTaskResponse(
                message_response=message_response,
                user_id=user_id,
                queries=queries,
            )
            
                        
        except Exception as e:
            raise HTTPException(status_code=500, detail="generate_response_failed") from e
                               

async def post_processing(user_id: str, queries: List[Any]) -> None:
    """
    Run post-interaction updates after a message exchange.

    Pipeline
    --------
    1) Post-processing refresh
       - Ask the model for: updated user summary, extrinsic relationship,
         sentiment deltas toward the user, and updated agent identity/self-perception.
       - Apply sentiment deltas and persist summary/relationship/identity.

    2) Episodic memory extraction (optional)
       - Ask the model whether this interaction should be stored in long-term memory.
       - If so, create a Memory entry and update tag inventory.

    3) Thought update (optional)
       - Ask the model for a refreshed agent thought; persist if provided.

    Parameters
    ----------
    user_id : str
        The target user's id.
    queries : List[Any]
        The running LLM transcript/messages. This function appends diagnostics to it.

    Notes
    -----
    - Uses concurrent I/O where safe to reduce latency.
    - Timestamps are UTC.
    - Defensively guards schema keys from the model.
    - Collects step timings for debug observability.
    """
    timings: Dict[str, float] = {}
    t0 = time.perf_counter()
    
    try:
        # ---------- Prefetch user/self concurrently ----------
        step_start = time.perf_counter()
        user_task = asyncio.create_task(grab_user(user_id))
        self_task = asyncio.create_task(grab_self())
        user, self = await asyncio.gather(user_task, self_task)
        timings["prefetch_user_self"] = time.perf_counter() - step_start
        
        # ---------- 1) Post-processing refresh ----------
        step_start = time.perf_counter()
        prompt = {
                    "role": USER_ROLE,
                    "content": (
                        build_post_processing_prompt(user, EXTRINSIC_RELATIONSHIPS)
                    ),
                }
        response = await structured_query(queries + [prompt], post_processing_schema(), False)
        response = _as_dict(response)
        
        queries.append({"role": BOT_ROLE, "content": f" This is {AGENT_NAME}'s refreshed summary of {user_id}, updated extrinsic relationship with {user_id}, sentiment change towards {user_id}, and updated self-perception: {json.dumps(response)}"})
        
        # Apply sentiment deltas (defensive default)
        sentiment_deltas = response.get("sentiment_deltas") or {}
        await alter_sentiments(sentiment_deltas, user)
        
        summary = response.get("summary") or user.get("summary", "")
        extrinsic_relationship = response.get("extrinsic_relationship") or user.get("extrinsic_relationship", "stranger")
        identity = response.get("identity") or self.get("identity", "")
        await update_summary_identity_relationship(
            user_id,
            summary,
            extrinsic_relationship,
            identity,
        )
        
        timings["post_processing_refresh"] = time.perf_counter() - step_start
           
        # ---------- 2) Create memory (optional) ----------
        step_start = time.perf_counter() 
        prompt = {
            "role": USER_ROLE, 
            "content": build_memory_prompt(self.get("memory_tags") or [])
        }
            
        response = await structured_query(queries + [prompt], get_memory_schema_lite(), quality=False)
        response = _as_dict(response)
        
        created_memory = False
        if response:
            event = response.get("event")
            thoughts = response.get("thoughts")
            
            if event and thoughts:
                tags = [t for t in (response.get("tags") or []) if t]
                # Normalize & cap tags (first 3)
                tags = tags[:3]
                
                mem = Memory(
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event=event,
                    thoughts=thoughts,
                    significance=response.get("significance", "low"),
                    emotional_impact=normalize_emotional_impact_fill_zeros(response.get("emotional_impact")),
                    tags=tags,
                )
            
                await asyncio.gather(
                        add_memory(mem),
                        update_tags(tags),
                    )

                created_memory = True
        
        timings["memory_creation"] = time.perf_counter() - step_start
            
        queries.append({"role": BOT_ROLE, "content": f"This is the decision on whether this interaction should be stored in {AGENT_NAME}'s long-term memory, and the episodic memory if so:{json.dumps(response)}"})
            
        # ---- 3) Update thought ----------------------------------------------
        step_start = time.perf_counter() 
        previous_thought = await get_thoughts(1)
        
        prompt = {
            "role": USER_ROLE,
            "content": (
                build_message_thought_prompt(self, previous_thought)
            )
        }
        
        response = await structured_query(queries + [prompt], get_thought_schema())
        
        thought_text = (response or {}).get("thought")
        
        if thought_text and str(thought_text).lower() != "no":
            await add_thought({
                "thought": thought_text,
                "timestamp": datetime.now(timezone.utc),
            })
              
        timings["updatthought_updateng_thought"] = time.perf_counter() - step_start
        
        # ---------- finalize ----------
        timings["total_post_processing"] = time.perf_counter() - t0
        if DEBUG_MODE:
            print("\nStep timings (seconds):")
            for step, duration in timings.items():
                print(f"{step}: {duration:.4f}")
                
            print("\nPost Processing Query List")
            print(queries)
        
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail="post_processing_failed") from e
    

def alter_personality(personality_deltas, self) -> Any:
    # Convert existing DB personality_matrix -> PersonalityMatrix
    flat = self["personality"].get("personality_matrix", {})
    normalized_deltas = _normalize_delta_payload(personality_deltas, set(flat.keys()))
    if not normalized_deltas.get("deltas"):
        print("Personality was not altered. No deltas.")
        return self["personality"]

    mat = PersonalityMatrix(traits={k: BoundedTrait(**v) for k, v in flat.items()})
    
    # Apply
    new_mat = apply_deltas_personality(
        mat, PersonalityDelta(**normalized_deltas), cap=3.0  # personality changes are slower
    )
    
    # Put back into the persisted shape
    self["personality"]["personality_matrix"] = {
        k: new_mat.traits[k].model_dump() if k in new_mat.traits else v
        for k, v in flat.items()
    }
    
    return self["personality"]

async def alter_emotions(emotion_deltas, self) -> Any:
    current = self["emotional_status"]
    normalized_deltas = _normalize_delta_payload(emotion_deltas, set(current["emotions"].keys()))
    if not normalized_deltas.get("deltas"):
        print("Emotions were not altered. No deltas.")
        return self["emotional_status"]

    emo = EmotionalState(
        emotions={k: BoundedTrait(**v) for k, v in current["emotions"].items()},
        reason=current.get("reason")
    )
    new_state = apply_deltas_emotion(emo, EmotionalDelta(**normalized_deltas), cap=7.0)
    # persist back in your DB shape
    self["emotional_status"]["emotions"] = {
        k: new_state.emotions[k].model_dump() for k in new_state.emotions
    }
    if new_state.reason:
        self["emotional_status"]["reason"] = new_state.reason
 
    await update_agent_emotions(self["emotional_status"])
    
    return self["emotional_status"]

async def alter_sentiments(sentiment_deltas, user)-> None:
    # Convert existing DB sentiment_status -> SentimentMatrix
    flat = user["sentiment_status"]
    normalized_deltas = _normalize_delta_payload(sentiment_deltas, set(flat["sentiments"].keys()))
    if not normalized_deltas.get("deltas"):
        print("Sentiments were not altered. No deltas.")
        return

    mat = SentimentMatrix(
        sentiments={k: BoundedTrait(**v) for k, v in flat["sentiments"].items()},
        reason=flat.get("reason")
    )
            
    # Apply
    new_mat = apply_deltas_sentiment(
        mat, SentimentDelta(**normalized_deltas), cap=5.0  # sentiment changes are slower
    )
    
    # Put back into the persisted shape        
    user["sentiment_status"]["sentiments"] = {
        k: new_mat.sentiments[k].model_dump() for k in new_mat.sentiments
    }
    if new_mat.reason:
        user["sentiment_status"]["reason"] = new_mat.reason

    await update_user_sentiment(user["user_id"], user["sentiment_status"])

async def check_implicit_addressed(user_id: str, username: str, message: str, recent_all_messages: Any) -> bool:
    implicit_addressing_result = await structured_query([{
            "role": USER_ROLE, 
            "content": (
                build_implicit_addressing_prompt(
                    message_memory=recent_all_messages, 
                    new_message=message, 
                    sender_id=user_id, 
                    sender_username=username
                )
            )
        }], implicitly_addressed_schema())
    implicit_addressing_result = _as_dict(implicit_addressing_result)
    
    return implicit_addressing_result.get("implicitly_addressed") == "yes"
