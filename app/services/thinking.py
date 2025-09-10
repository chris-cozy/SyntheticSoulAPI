import asyncio
from datetime import datetime
import json
from typing import Any, List

from app.constants.constants import BOT_ROLE, SYSTEM_MESSAGE, USER_ROLE
from app.core.config import AGENT_NAME, CONVERSATION_MESSAGE_RETENTION_COUNT, DEBUG_MODE, MESSAGE_HISTORY_COUNT, THINKING_RATE
from app.constants.schemas import get_initiate_messages_schema, get_thought_schema, get_emotion_delta_schema_lite, get_memory_schema_lite, get_message_appropriate_schema
from app.domain.memory import Memory
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState
from app.services.database import add_memory, add_thought, get_all_message_memory, get_conversation, grab_self, grab_user, insert_message_to_conversation, insert_message_to_message_memory, update_agent_emotions, update_agent_expression, update_tags
from app.services.memory import get_random_memory_tag, normalize_emotional_impact_fill_zeros, retrieve_relevant_memory_from_tag
from app.services.message_processor import alter_emotions
from app.services.openai import get_structured_response
from app.services.prompting import _system_message, build_emotion_delta_prompt_thinking, build_initiate_message_prompt, build_memory_prompt, build_message_appropriate_prompt, build_thought_prompt
from app.services.state_reducer import apply_deltas_emotion

async def generate_thought():
    """
    Generates a thought that the agent is having, and inputs it in the database
    """
    recent_all_messages = await get_all_message_memory(MESSAGE_HISTORY_COUNT)
    self = await grab_self()
    thought_queries = [SYSTEM_MESSAGE]
    thought_queries = [_system_message(personality=self["personality"], emotions=self["emotional_status"], identity=self["identity"])]

    # ---- 0) Retrieve Random Memories -------------------------------------------
    memory_tag = get_random_memory_tag(self)
    
    retrieved_memory = await retrieve_relevant_memory_from_tag(memory_tag)
    
    
    # ---- 1) Check Thought -------------------------------------------
    prompt = {
        "role": USER_ROLE,
        "content": (
            build_thought_prompt(self, recent_all_messages, retrieved_memory)
        )
    }
    
    current_thought = await get_structured_response(thought_queries + [prompt], get_thought_schema())
    
    if current_thought["thought"] == "no":
        return
    
    if current_thought["new_expression"] != "no":
        await update_agent_expression(current_thought["new_expression"])
    
    thought_queries.append({"role": BOT_ROLE, "content": f"This is what {AGENT_NAME} is currently thinking: {json.dumps(current_thought)}"})
    
    await add_thought(
        {
            "thought": current_thought['thought'],
            "timestamp": datetime.now()
        } 
    )
    
    # ---- 1.5) Initiate Message -------------------------------------------
    prompt = {
        "role": USER_ROLE,
        "content": (
            build_initiate_message_prompt()
        )
    }
    
    initiate_messages = await get_structured_response(thought_queries + [prompt], get_initiate_messages_schema())
    
    if await handle_initiating_messages(initiate_messages["initiate_messages"]):
        thought_queries.append({"role": BOT_ROLE, "content": f"These are the messages {AGENT_NAME} has initiated: {json.dumps(initiate_messages)}"})
    
    
    # ---- 2) Thought Emotional Reaction -------------------------------------------
    prompt = {
        "role": USER_ROLE,
        "content": (
            build_emotion_delta_prompt_thinking(
                agent=self,
                latest_thought=current_thought['thought']
            )
        )
    }
    
    delta = await get_structured_response(
        [_system_message(personality=self["personality"], emotions=self["emotional_status"], identity=self["identity"]), prompt],
        get_emotion_delta_schema_lite(),
        quality=False
    )
    
    current_emotions = await alter_emotions(delta, self)
    
    thought_queries.append({"role": BOT_ROLE, "content":f"This is the emotional effect {AGENT_NAME}'s latest thought had on them: {json.dumps(delta)}"})

    # ---- 3) Memory Creation -------------------------------------------
    prompt = {
            "role": USER_ROLE, 
            "content": build_memory_prompt(self['memory_tags'])
        }
    
    memory_response = await get_structured_response(thought_queries + [prompt], get_memory_schema_lite(), quality=False)
    
    if memory_response and memory_response.get("event") and memory_response.get("thoughts"):
        mem = Memory(
            agent_name=AGENT_NAME,
            user_id=None,
            event=memory_response["event"],
            thoughts=memory_response["thoughts"],
            significance=memory_response.get("significance", "low"),
            emotional_impact=normalize_emotional_impact_fill_zeros(memory_response.get("emotional_impact")),
            tags=[t for t in (memory_response.get("tags") or []) if t][:3],
        )
        
        await add_memory(mem)
        await update_tags(memory_response.get("tags") or []) 
        
    if DEBUG_MODE:
        print("\nThought Query List")
        print(thought_queries)
    
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
        
async def handle_initiating_messages(messages: List[Any]) -> bool:
    if not messages:
        return False
        
    for message in messages:
        user = await grab_user(message["user_id"])
        self = await grab_self()
        conversation = await get_conversation(message["user_id"])
        recent_user_messages = conversation["messages"][-5:] if "messages" in conversation else []
        if not user:
            continue
        
        # Check if message is appropriate to send
        prompt = {
            "role": USER_ROLE,
            "content": (
                build_message_appropriate_prompt(
                    self=self,
                    user=user,
                    message=message,
                    recent_user_messages=recent_user_messages,
                )
            )
        }
        message_response = await get_structured_response(
            [prompt], get_message_appropriate_schema(), quality=True)
        
        if message_response["message"] == "no":
            continue
        
        rich_message = {
                "message": message_response["message"],
                "purpose": message["purpose"],
                "tone": message["tone"],
                "timestamp": datetime.now(),
                "sender_id": AGENT_NAME,
                "sender_username": AGENT_NAME,
                "from_agent": True
            }
        
        await insert_message_to_conversation(
            message["user_id"], 
            rich_message
        )
        
        await insert_message_to_message_memory(rich_message)
        
    return True
        