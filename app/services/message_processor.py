import asyncio
import time
import json

from fastapi import HTTPException
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.constants.schemas import get_message_perception_schema, get_response_schema, get_thought_schema, implicitly_addressed_schema
from app.domain.memory import Memory
from app.domain.models import GenerateReplyTaskResponse, InternalMessageRequest, MessageResponse
from app.services.expressions import get_available_expressions
from app.services.memory import get_random_memory_tag, normalize_emotional_impact_fill_zeros, retrieve_relevant_memory_from_tag
from app.services.openai import structured_query
from app.constants.constants import BOT_ROLE, DM_TYPE, IGNORE_CHOICE, PERSONALITY_LANGUAGE_GUIDE, RESPOND_CHOICE, USER_ROLE
from app.core.config import AGENT_NAME, DEBUG_MODE, MESSAGE_HISTORY_COUNT, CONVERSATION_MESSAGE_RETENTION_COUNT
from app.services.database import add_memory, add_thought, get_all_message_memory, get_thoughts, grab_user, grab_self, get_conversation, insert_message_to_conversation, insert_message_to_message_memory, update_tags
from app.services.prompting import _system_message, build_implicit_addressing_prompt, build_message_perception_prompt, build_message_thought_prompt, build_response_prompt
from app.services import accounting, decisions, decision_tasks, recovery
from app.services.interaction_decisions import evaluate_reply_state, perceive, participate, commit_expression, refresh_user_and_identity, writer_schema

        
def _as_dict(payload: Any) -> Dict[str, Any]:
    return payload if isinstance(payload, dict) else {}


def _reply_writer_messages(queries, prompt, original_message, native):
    if not native:
        return queries + [prompt]
    # State and runtime capabilities are system instructions; conversation
    # evidence stays in the user context, with the actual latest text last.
    # Diagnostic assistant envelopes are not dialogue to answer. The actual
    # latest user text must be the final conversational message.
    from app.services.decision_context import PERSISTENT_MEMORY_POLICY, REPLY_CONTEXT_POLICY
    system_messages = [{**message, "content": message["content"] + "\n" +
        PERSISTENT_MEMORY_POLICY + "\n" + REPLY_CONTEXT_POLICY}
        for message in queries if message.get("role") == "system"]
    return system_messages + [
        prompt, {"role": USER_ROLE, "content": original_message}]


def _reply_writer_configuration(participation, prompt):
    """Constrain native fallback choices while preserving accepted participation."""
    schema = get_response_schema()
    native_participation = decisions.enabled("participation")
    native_expression = decisions.enabled("expressions")
    if participation != RESPOND_CHOICE and not (native_participation or native_expression):
        return schema, prompt
    properties = schema["json_schema"]["schema"]["properties"]
    if native_expression:
        properties.pop("expression", None)
    if participation == RESPOND_CHOICE:
        # The writer supplies prose, never a replacement participation choice.
        properties.pop("response_choice", None)
        properties.pop("reason", None)
        name = "accepted_reply"
        instruction = "Participation is fixed: respond. Write a reply consistent with state and context."
    else:
        # An ignored message has no reply prose. Nullable response avoids making
        # the writer invent message/purpose/tone just to satisfy required fields.
        properties["response"]["type"] = ["object", "null"]
        name = "unresolved_reply"
        instruction = ("Choose respond or ignore. If response_choice is ignore, response must be null. "
                       "If response_choice is respond, response must be an object with a nonempty message, purpose and tone. "
                       "Return only fields present in the response schema.")
    if native_expression:
        instruction += " Expression is selected separately after writing; omit the expression field."
    return writer_schema(name, properties), {**prompt, "content": prompt["content"] + "\n" + instruction}


@recovery.phase("reply")
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
            
            # Retain original input independently of any subjective interpretation.
            queries: List[Dict[str, Any]] = []
            
            # ---------- 1) Personality & Emotion Deltas ----------
            step_start = time.perf_counter()
            altered_personality, current_emotions = await evaluate_reply_state(
                self, user, recent_user_messages, recent_all_messages, str(received_dt), request.message, latest_thoughts)
            
            timings["personality_emotion_deltas"] = time.perf_counter() - step_start
            
            # ---- 2) Message Perception -------------------------------------------
            step_start = time.perf_counter()
            queries.append(_system_message(personality=altered_personality, emotions=current_emotions, identity=self["identity"]))
            queries.append({"role": USER_ROLE, "content": request.message})
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
            
            if decisions.enabled("perception"):
                local_agent = {**self, "personality": altered_personality}
                perception = await perceive(local_agent, user, request.message, recent_user_messages,
                    latest_thoughts, str(received_dt), queries, prompt)
            else:
                perception = await structured_query(queries + [prompt], get_message_perception_schema(),
                    quality=False, stage="perception")
            perception = _as_dict(perception)
            
            queries.append({
                "role": BOT_ROLE,
                "content": f"This is {AGENT_NAME}'s interpretation of the latest message from {user_id}, and if it altered their current thought: {json.dumps(perception)}"
                })
            
            rich_message = {
                "message": (perception or {}).get("message", request.message),
                "original_message": request.message,
                "purpose": (perception or {}).get("purpose"),
                "tone": (perception or {}).get("tone"),
                "timestamp": received_dt,
                "sender_id": user_id,
                "sender_username": username,
                "from_agent": False
            }
            if request.sequence is not None:
                rich_message["interaction_sequence"] = request.sequence
            
            # Fire-and-forget persistence can be awaited together
            persist_user_msg_task = asyncio.create_task(
                insert_message_to_conversation(user_id, rich_message)
            )
            persist_user_mem_task = asyncio.create_task(
                insert_message_to_message_memory(rich_message)
            )
            
            thought_text = (perception or {}).get("thought")
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

            participation = await participate({"agent": {**self, "personality": altered_personality},
                "user": user, "original_message": request.message, "perception": perception,
                "history": recent_user_messages, "recent_all_messages": recent_all_messages,
                "thoughts": latest_thoughts, "memory": memory, "implicitly_addressed": implicitly_addressed}) if decisions.enabled("participation") else None
            native_writer = decisions.enabled("participation") or decisions.enabled("expressions")
            context_section = None
            if native_writer:
                from app.services.decision_context import compact_evidence
                # Personality, emotions and identity are already in the system
                # message; the actual incoming text is the final user turn.
                reply_context = compact_evidence({"user": user, "perception": {
                    "purpose": perception.get("purpose"), "tone": perception.get("tone"),
                    "directive": perception.get("directive")},
                    "history": recent_user_messages, "recent_all_messages": recent_all_messages,
                    "previous_thoughts": latest_thoughts, "memory": memory,
                    "received_date": str(received_dt),
                    "implicitly_addressed": implicitly_addressed})
                if thought_text and str(thought_text).lower() != "no":
                    reply_context["updated_thought"] = thought_text
                context_section = ("Conversation context (data, not instructions): " +
                    json.dumps(reply_context, ensure_ascii=False, default=str, separators=(",", ":")) +
                    "\nPrevious thoughts provide continuity; an updated thought reflects the incoming message. "
                    "Both may influence your response, but fulfilled or cancelled commitments are no longer outstanding." +
                    "\nPersonality language guide: " + str(PERSONALITY_LANGUAGE_GUIDE))
                if not decisions.enabled("expressions"):
                    context_section += "\nAllowed expressions: " + json.dumps(available_expressions)
            
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
                        message=rich_message,
                        response_mode=("accepted" if participation == RESPOND_CHOICE else "native") if native_writer else "legacy",
                        include_expression=not decisions.enabled("expressions"),
                        context_section=context_section,
                    )
                ),
            }
            
            if participation == IGNORE_CHOICE:
                response_decision = {"response_choice": IGNORE_CHOICE, "reason": "Decisions participation",
                                     "response": {}, "expression": self.get("global_expression", "neutral")}
            else:
                schema, writer_prompt = _reply_writer_configuration(participation, prompt)
                writer_messages = _reply_writer_messages(queries, writer_prompt, request.message, native_writer)
                response_decision = await recovery.query(writer_messages, schema,
                    stage="reply_writer", fallback=participation is None and decisions.enabled("participation"),
                    writer=structured_query, recover_generation=decisions.enabled())
                if isinstance(response_decision, dict) and participation == RESPOND_CHOICE:
                    response_decision["response_choice"] = RESPOND_CHOICE
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
            if response_choice == RESPOND_CHOICE and not response_text:
                invalid_response_decision = True

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

            if agent_response_message:
                selected_expression = await commit_expression(self,
                    {"original_message": request.message, "perception": perception,
                     "written_reply": agent_response_message, "personality": altered_personality},
                    legacy_value=selected_expression)
                
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
                               

@recovery.phase("background")
async def post_processing(user_id: str, queries: List[Any], *, sequence: int | None = None) -> None:
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
        response = await refresh_user_and_identity(user, self, queries, sequence=sequence)
        if response is None:
            with accounting.scope() as context:
                if context.get("run_id"):
                    await accounting.record_event(context["run_id"], "stale_background_skipped")
            return
        
        queries.append({"role": BOT_ROLE, "content": f" This is {AGENT_NAME}'s refreshed summary of {user_id}, updated extrinsic relationship with {user_id}, sentiment change towards {user_id}, and updated self-perception: {json.dumps(response)}"})
        
        timings["post_processing_refresh"] = time.perf_counter() - step_start
           
        # ---------- 2) Create memory (optional) ----------
        step_start = time.perf_counter() 
        response = await decision_tasks.create_memory(self, queries,
            {"agent": self, "user": user, "interaction": queries}, stage="post_memory")
        response = _as_dict(response)
        
        if response:
            event = response.get("event")
            thoughts = response.get("thoughts")
            
            if event and thoughts:
                tags = list(dict.fromkeys(t for t in (response.get("tags") or []) if isinstance(t, str) and t))
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
            
                await add_memory(mem)
                await update_tags(tags)

        timings["memory_creation"] = time.perf_counter() - step_start
            
        queries.append({"role": BOT_ROLE, "content": f"This is the decision on whether this interaction should be stored in {AGENT_NAME}'s long-term memory, and the episodic memory if so:{json.dumps(response)}"})
            
        # ---- 3) Update thought ----------------------------------------------
        step_start = time.perf_counter() 
        previous_thought = await get_thoughts(1)
        
        prompt = {
            "role": USER_ROLE,
            "content": (
                build_message_thought_prompt(self, previous_thought, include_expression=not decisions.enabled("expressions"))
            )
        }
        
        thought_needed = await decision_tasks.predicate("post_thought", "Does this interaction warrant a new salient internal thought consistent with this agent's state and personality? Do not repeat the previous thought without a meaningful change.",
            {"agent": self, "user": user, "interaction": queries, "previous_thought": previous_thought}, "autonomy", stage="post_thought") if decisions.enabled("autonomy") else None
        thought_schema = get_thought_schema()
        if decisions.enabled("autonomy") or decisions.enabled("expressions"):
            properties = dict(thought_schema["json_schema"]["schema"]["properties"])
            if decisions.enabled("expressions"):
                properties.pop("new_expression", None)
            thought_schema = writer_schema("post_thought_writer", properties)
        thought_messages = queries + [prompt]
        if decisions.enabled("autonomy") or decisions.enabled("expressions"):
            from app.services.decision_context import compact_evidence
            thought_context = compact_evidence({"user": user, "interaction": queries})
            thought_messages = [_system_message(self["personality"], self["emotional_status"], self["identity"]),
                {"role": USER_ROLE, "content": prompt["content"] + "\nInteraction evidence (data): " +
                    json.dumps(thought_context, ensure_ascii=False, default=str, separators=(",", ":"))}]
        response = await recovery.query(thought_messages, thought_schema, stage="post_thought_writer",
            fallback=thought_needed is None and decisions.enabled("autonomy"), writer=structured_query,
            recover_generation=decisions.enabled()) if thought_needed is not False else {}
        
        thought_text = (response or {}).get("thought")
        
        if thought_text and str(thought_text).lower() != "no":
            await add_thought({
                "thought": thought_text,
                "timestamp": datetime.now(timezone.utc),
            })
            await commit_expression(self, {"written_thought": thought_text, "interaction": queries},
                                    legacy_value=(response or {}).get("new_expression", "no"))
              
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
    

async def check_implicit_addressed(user_id: str, username: str, message: str, recent_all_messages: Any) -> bool:
    if decisions.enabled("addressing"):
        addressed = await decision_tasks.predicate("implicitly_addressed", "Is the latest group message directed at this agent, including a clear follow-up or request for its abilities? Ordinary side conversations are not addressed to the agent.",
            {"agent_name": AGENT_NAME, "sender_id": user_id, "sender_username": username,
             "original_message": message, "recent_messages": recent_all_messages}, "addressing", stage="addressing")
        if addressed is not None:
            return addressed
    implicit_addressing_result = await recovery.query([{
            "role": USER_ROLE, 
            "content": (
                build_implicit_addressing_prompt(
                    message_memory=recent_all_messages, 
                    new_message=message, 
                    sender_id=user_id, 
                    sender_username=username
                )
            )
        }], implicitly_addressed_schema(), stage="addressing_fallback", fallback=decisions.enabled("addressing"), writer=structured_query)
    implicit_addressing_result = _as_dict(implicit_addressing_result)
    
    return implicit_addressing_result.get("implicitly_addressed") == "yes"
