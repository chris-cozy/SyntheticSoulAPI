import asyncio
import os
import random
from app.constants.constants import EMOTIONAL_DECAY_RATE
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState
from app.services.database import grab_self, update_agent_emotions
from app.services.state_reducer import apply_deltas_emotion, apply_deltas_emotional_friction

agent_name = os.getenv("BOT_NAME")

async def emotion_decay_loop(decay_rate: int, lite_mode: bool):
    '''
        Decrease all emotions by 1

        :param decay_rate: The number of seconds between each loop of the function
        :param lite_mode: Whether we are dealing with lite_mode emotions
    '''
    while True:
        try:
            self = await grab_self(agent_name, lite_mode)
            
            current = self["emotional_status"]
            emo = EmotionalState(
                emotions={k: BoundedTrait(**v) for k, v in current["emotions"].items()},
                reason=current.get("reason")
            )
            # build a small negative delta only for > min values
            deltas = {}
            for k, t in emo.emotions.items():
                if int(t.value) > int(t.min):
                    deltas[k] = -1
            if deltas:
                decayed = apply_deltas_emotional_friction(
                    emo, 
                    EmotionalDelta(deltas=deltas, reason="decay", confidence=1.0), cap=7.0
                )
                
                # Persist back as INTs (validator requires bsonType: "int")
                self["emotional_status"]["emotions"] = {
                    k: decayed.emotions[k].model_dump() for k in decayed.emotions
                }
                if decayed.reason:
                    self["emotional_status"]["reason"] = decayed.reason
                
                await update_agent_emotions(self["name"], self["emotional_status"])     
    
        except Exception as e:
            print(f"Error - Emotional decay: {e}")

        await asyncio.sleep(decay_rate)

async def start_emotion_decay():
    '''
        Start the emotional decay loop
    '''
    await emotion_decay_loop(EMOTIONAL_DECAY_RATE, True)
    
    
def get_random_memories(self):
    """
    Selects a random memory or group of memories
    
    Parameters:
        self (object): The object of the AI agent.
        
    Returns:
        array: An array of the selected memories
    """
    significances = ['high', 'medium', 'low']
    weights = [0.7, 0.2, 0.1]
    chosen_significance = random.choices(significances, weights=weights, k=1)
    
    filtered_memories = []
    selected_memories = []
    for memory in self['memory_profile']['memories']:
        if memory['significance'] == chosen_significance[0]:
            filtered_memories.append(memory)
            
    if (len(filtered_memories) > 0):
        all_tags = set()
        
        for memory in filtered_memories:
            all_tags.update(memory["tags"])
            
        random_tag = random.choice(list(all_tags))
        
        matching_memories = [memory for memory in filtered_memories if random_tag in memory["tags"]]
        
        selected_memories = matching_memories
        
        if len(matching_memories) >= 2:
            selected_memories = random.sample(matching_memories, 2)
            
    return selected_memories


