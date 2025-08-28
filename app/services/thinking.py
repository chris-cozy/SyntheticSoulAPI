from datetime import datetime
import os

from app.constants.constants import MESSAGE_HISTORY_COUNT, SYSTEM_MESSAGE, USER_ROLE
from app.constants.schemas import get_thought_schema
from app.services.data_service import add_thought, get_message_memory, grab_self
from app.services.openai_service import get_structured_response
from app.services.prompt_service import build_thought_prompt
from app.services.util_service import get_random_memories

agent_name = os.getenv("BOT_NAME")

async def generate_thought():
    """
    Generates a thought that the agent is having, and inputs it in the database
    """
    recent_all_messages = await get_message_memory(agent_name, MESSAGE_HISTORY_COUNT)
    self = await grab_self(agent_name, True)
    
    thought_prompt = {
        "role": USER_ROLE,
        "content": (
            build_thought_prompt(self, recent_all_messages, get_random_memories(self))
        )
    }
    
    current_thought = await get_structured_response([SYSTEM_MESSAGE, thought_prompt], get_thought_schema())
    
    await add_thought(
        agent_name, 
        {
            "thought": current_thought['thought'],
            "timestamp": datetime.now()
        } 
    )
    
async def periodic_thinking():
    """
    Starts the thinking process, for the assigned duration
    """
    while True:
        await generate_thought()