import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.constants.constants import AGENT_COLLECTION, AGENT_LITE_COLLECTION, AGENT_NAME_PROPERTY, MIN_EMOTION_VALUE, EMOTIONAL_DECAY_RATE
from app.services.data_service import get_database, grab_self

async def emotion_decay_loop(decay_rate: int, lite_mode: bool):
    '''
        Decrease all emotions by 1

        :param decay_rate: The number of seconds between each loop of the function
        :param lite_mode: Whether we are dealing with lite_mode emotions
    '''
    db = get_database()
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
                db[AGENT_LITE_COLLECTION].update_one({"name": self[AGENT_NAME_PROPERTY]}, { "$set": {"emotional_status": self["emotional_status"] }})
            else: 
                db[AGENT_COLLECTION].update_one({"name": self[AGENT_NAME_PROPERTY]}, { "$set": {"emotional_status": self["emotional_status"] }})

        except Exception as e:
            print(f"Error - Emotional decay: {e}")

        # Wait for the specified decay rate
        await asyncio.sleep(decay_rate)

async def start_emotion_decay():
    '''
        Start the emotional decay loop
    '''
    await emotion_decay_loop(EMOTIONAL_DECAY_RATE, True)

