import asyncio
from datetime import datetime
import json

from app.constants.constants import BOT_ROLE, SYSTEM_MESSAGE, USER_ROLE
from app.core.config import AGENT_NAME, MESSAGE_HISTORY_COUNT, THINKING_RATE
from app.constants.schemas import get_thought_schema
from app.constants.schemas_lite import get_emotion_delta_schema_lite, get_memory_schema_lite
from app.domain.memory import Memory
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState
from app.services.database import add_memory, add_thought, get_all_message_memory, grab_self, update_agent_emotions, update_tags
from app.services.memory import get_random_memory_tag, normalize_emotional_impact_fill_zeros, retrieve_relevant_memory_from_tag
from app.services.openai import get_structured_response
from app.services.prompting import build_emotion_delta_prompt_thinking, build_memory_prompt, build_thought_prompt
from app.services.state_reducer import apply_deltas_emotion

async def generate_thought():
    """
    Generates a thought that the agent is having, and inputs it in the database
    """
    recent_all_messages = await get_all_message_memory(MESSAGE_HISTORY_COUNT)
    self = await grab_self()
    thought_queries = [SYSTEM_MESSAGE]

    # ---- 0) Retrieve Random Memories -------------------------------------------
    memory_tag = get_random_memory_tag(self)
    
    retrieved_memory = await retrieve_relevant_memory_from_tag(memory_tag)
    
    
    # ---- 1) Check Thought -------------------------------------------
    thought_prompt = {
        "role": USER_ROLE,
        "content": (
            build_thought_prompt(self, recent_all_messages, retrieved_memory)
        )
    }
    thought_queries.append(thought_prompt)
    
    current_thought = await get_structured_response(thought_queries, get_thought_schema())
    
    thought_queries.append({"role": BOT_ROLE, "content": json.dumps(current_thought)})
    
    if current_thought["thought"] == "no":
        return
    
    await add_thought(
        {
            "thought": current_thought['thought'],
            "timestamp": datetime.now()
        } 
    )
    
    # ---- 2) Thought Emotional Reaction -------------------------------------------
    prompt = {
        "role": USER_ROLE,
        "content": (
            build_emotion_delta_prompt_thinking(
                personality=self["personality"],
                emotional_status=self["emotional_status"],
                latest_thought=current_thought['thought']
            )
        )
    }
    thought_queries.append(prompt)
    
    delta = await get_structured_response(
        [prompt],
        get_emotion_delta_schema_lite(),
        quality=False
    )
    
    thought_queries.append({"role": BOT_ROLE, "content": json.dumps(delta)})
    
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
    
    # ---- 3) Memory Creation -------------------------------------------
    thought_queries.append({
            "role": USER_ROLE, 
            "content": build_memory_prompt(self['memory_tags'])
        })
        
    memory_response = await get_structured_response(thought_queries, get_memory_schema_lite(), quality=False)
    
    if memory_response and memory_response.get("event") and memory_response.get("thoughts"):
        mem = Memory(
            agent_name=AGENT_NAME,
            user=None,
            event=memory_response["event"],
            thoughts=memory_response["thoughts"],
            significance=memory_response.get("significance", "low"),
            emotional_impact=normalize_emotional_impact_fill_zeros(memory_response.get("emotional_impact")),
            tags=[t for t in (memory_response.get("tags") or []) if t][:3],
        )
        
        await add_memory(mem)
        await update_tags(memory_response.get("tags") or []) 
    
async def periodic_thinking():
    """
    Starts the thinking process, for the assigned duration
    """
    while True:
        try:
            await generate_thought()
        except Exception as e:
            print(f"Error in generate_thought: {e}")
        await asyncio.sleep(THINKING_RATE)