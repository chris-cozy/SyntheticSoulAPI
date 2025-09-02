import asyncio
from app.core.config import AGENT_NAME, EMOTIONAL_DECAY_RATE
from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState
from app.services.database import grab_self, update_agent_emotions
from app.services.state_reducer import apply_deltas_emotional_decay

async def emotion_decay_loop(decay_rate: int = EMOTIONAL_DECAY_RATE):
    '''
        Decrease all emotions by 1

        :param decay_rate: The number of seconds between each loop of the function
        :param lite_mode: Whether we are dealing with lite_mode emotions
    '''
    while True:
        try:
            self = await grab_self()
            
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
                decayed = apply_deltas_emotional_decay(
                    emo, 
                    EmotionalDelta(deltas=deltas, reason="decay", confidence=1.0), cap=7.0
                )
                
                # Persist back as INTs (validator requires bsonType: "int")
                self["emotional_status"]["emotions"] = {
                    k: decayed.emotions[k].model_dump() for k in decayed.emotions
                }
                if decayed.reason:
                    self["emotional_status"]["reason"] = decayed.reason
                
                await update_agent_emotions(self["emotional_status"])     
    
        except Exception as e:
            print(f"Error - Emotional decay: {e}")

        await asyncio.sleep(decay_rate)



