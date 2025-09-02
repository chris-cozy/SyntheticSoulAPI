import random
from typing import Optional, Dict
from app.constants.constants import (
    BASE_EMOTIONAL_STATUS_LITE,
    MIN_EMOTION_VALUE,
    MAX_EMOTION_VALUE,
)
from app.services.database import get_tagged_memories

EMOTION_KEYS = tuple(BASE_EMOTIONAL_STATUS_LITE["emotions"].keys())

def normalize_emotional_impact_fill_zeros(
    impact: Optional[Dict]
) -> Optional[Dict]:
    """
    If the LLM returns a partial emotional_impact (e.g., {"joy":{"value":35}})
    expand missing keys to {"value": 0}. If `impact` is None/empty, return None
    (saves storage and remains allowed by the validator).
    """
    if not impact:
        return None  # leave out entirely if LLM emitted nothing

    out: Dict[str, Dict[str, int]] = {}
    for k in EMOTION_KEYS:
        v = impact.get(k)
        if isinstance(v, dict) and ("value" in v) and (v["value"] is not None):
            try:
                val = int(v["value"])
            except Exception:
                val = 0
        else:
            val = 0

        # clamp to your global bounds
        if val < MIN_EMOTION_VALUE:
            val = MIN_EMOTION_VALUE
        if val > MAX_EMOTION_VALUE:
            val = MAX_EMOTION_VALUE

        out[k] = {"value": val}

    return out

def get_random_memory_tag(self) -> str | None:
    memory_tags = self.get("memory_tags", [])
    if not memory_tags:
        return None
    return random.choice(memory_tags)


async def retrieve_relevant_memory_from_tag(tag: str, count: int = 1):
    tagged_memories = await get_tagged_memories(tag)
    
    if not tagged_memories:
        return None
    
    # For now return random memory from the tag, can expand later
    return random.choice(tagged_memories)


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