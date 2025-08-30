import asyncio
import os
import random
from app.constants.constants import AGENT_NAME_PROPERTY, MIN_EMOTION_VALUE, EMOTIONAL_DECAY_RATE
from app.services.database import grab_self, update_agent_emotions

async def emotion_decay_loop(decay_rate: int, lite_mode: bool):
    '''
        Decrease all emotions by 1

        :param decay_rate: The number of seconds between each loop of the function
        :param lite_mode: Whether we are dealing with lite_mode emotions
    '''
    while True:
        try:
            self = await grab_self(os.getenv('BOT_NAME'), lite_mode)

            if not self:
                print(f"Warning - emotion_decay_loop: Self-agent {os.getenv('BOT_NAME')} not found ")
                await asyncio.sleep(decay_rate)
                continue

            emotions = self["emotional_status"]["emotions"]

            for emotion, data in emotions.items():
                if data["value"] > MIN_EMOTION_VALUE:
                    data["value"] -= 1
                    if data["value"] < 0:
                        data["value"] = 0

                    self["emotional_status"]["emotions"][emotion]["value"] = data["value"]

            if (lite_mode):
                await update_agent_emotions(self[AGENT_NAME_PROPERTY], self["emotional_status"])
            else: 
                await update_agent_emotions(self[AGENT_NAME_PROPERTY], self["emotional_status"], False)

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


