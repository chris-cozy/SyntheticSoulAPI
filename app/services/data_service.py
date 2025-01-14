import json
import os
from app.constants.constants import NO_INTRINSIC_RELATIONSHIP
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

db_client = None


async def init_db():
    global db_client
    mongo_uri = os.getenv('MONGO_CONNECTION')
    if not mongo_uri:
        raise RuntimeError("MONGO_CONNECTION environment variable is not set.")
    db_client = AsyncIOMotorClient(mongo_uri)
    print(f"Connected to MongoDB at {mongo_uri}")

def get_database():
    if db_client is None:
        raise RuntimeError("Database client is not initialized. Call `init_db()` first.")
    return db_client.get_database("SyntheticSoul-Dev")

async def grab_user(author_id, author_name):
    """
    Grab user object based on their Discord ID.
    If the user doesn't exist, create a new one with default values.

    :param author_id: Discord ID of the user
    :param author_name: Username of the user
    :return: User object
    """
    db = get_database()
    users_collection = db["users"]

    user = await users_collection.find_one({"discord_id": author_id})

    if not user:
        # Determine intrinsic relationship
        if author_id == os.getenv("DEVELOPER_ID"):
            intrinsic_relationship = "creator and master"
        else:
            intrinsic_relationship = NO_INTRINSIC_RELATIONSHIP
            
        # Create a new user if one doesn't exist
        new_user = {
            "name": author_name,
            "discord_id": author_id,
            "intrinsic_relationship": intrinsic_relationship,
        }
        result = await users_collection.insert_one(new_user)
        user = await users_collection.find_one({"_id": result.inserted_id})

    return user


async def grab_self(agent_name):
    """
    Grab self object based on the agent name.
    If the agent doesn't exist, create one with default values.

    :param agent_name: Name of the bot
    :return: Self object
    """
    db = get_database()
    self_collection = db["selves"]

    self = await self_collection.find_one({"name": agent_name})

    if not self:
        # Create a new self object if one doesn't exist
        new_self = {
            "name": agent_name,
            "personality_matrix": os.getenv("BOT_PERSONALITY_MATRIX"),
        }
        result = await self_collection.insert_one(new_self)
        self = await self_collection.find_one({"_id": result.inserted_id})

    return self


async def get_conversation(user_id):
    """
    Grab conversation messages based on the user ID.
    If no conversation exists, create a new conversation object.

    :param user_id: Discord ID of the user
    :return: Conversation object
    """
    db = get_database()
    conversations_collection = db["conversations"]

    user_conversation = await conversations_collection.find_one({"user_id": user_id})

    if not user_conversation:
        # Create a new conversation object if one doesn't exist
        new_conversation = {
            "user_id": user_id,
            "messages": []  # Initialize an empty list for messages
        }
        result = await conversations_collection.insert_one(new_conversation)
        user_conversation = await conversations_collection.find_one({"_id": result.inserted_id})

    return user_conversation


# Export functions for use
__all__ = ["grab_user", "grab_self", "get_conversation"]