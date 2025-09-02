import asyncio
from datetime import datetime
import os

from app.constants.constants import AGENT_NAME, MESSAGE_HISTORY_COUNT, SYSTEM_MESSAGE, USER_ROLE
from app.constants.schemas import get_thought_schema
from app.constants.schemas_lite import get_emotion_delta_schema_lite
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState
from app.services.database import add_thought, get_all_message_memory, grab_self, update_agent_emotions
from app.services.openai import get_structured_response
from app.services.prompting import build_emotion_delta_prompt_thinking, build_thought_prompt
from app.services.state_reducer import apply_deltas_emotion

agent_name = os.getenv("BOT_NAME")

async def generate_thought():
    """
    Generates a thought that the agent is having, and inputs it in the database
    """
    # ---- 0) Check Thought -------------------------------------------
    recent_all_messages = await get_all_message_memory(agent_name, MESSAGE_HISTORY_COUNT)
    self = await grab_self(agent_name, True)
    
    thought_prompt = {
        "role": USER_ROLE,
        "content": (
            build_thought_prompt(self, recent_all_messages, [])
        )
    }
    
    current_thought = await get_structured_response([SYSTEM_MESSAGE, thought_prompt], get_thought_schema())
    
    if current_thought["thought"] == "no":
        return
    
    await add_thought(
        agent_name, 
        {
            "thought": current_thought['thought'],
            "timestamp": datetime.now()
        } 
    )
    
    # ---- 1) Thought Emotional Reaction -------------------------------------------
    prompt = build_emotion_delta_prompt_thinking(
        AGENT_NAME,
        personality=self["personality"],
        emotional_status=self["emotional_status"],        # current values
        latest_thought=current_thought['thought']
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
    
    await update_agent_emotions(AGENT_NAME, current_emotions)    
    
async def periodic_thinking():
    """
    Starts the thinking process, for the assigned duration
    """
    while True:
        try:
            await generate_thought()
        except Exception as e:
            print(f"Error in generate_thought: {e}")
        await asyncio.sleep(180)