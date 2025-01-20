from datetime import datetime
import os
from app.constants.constants import AGENT_COLLECTION, AGENT_LITE_COLLECTION, BASE_EMOTIONAL_STATUS, BASE_EMOTIONAL_STATUS_LITE, BASE_PERSONALITIES_LITE, BASE_PERSONALITY, BASE_SENTIMENT_MATRIX, BASE_SENTIMENT_MATRIX_LITE, CONVERSATION_COLLECTION, INTRINSIC_RELATIONSHIPS, MESSAGE_MEMORY_COLLECTION, USER_COLLECTION, USER_LITE_COLLECTION
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.agent import AGENT_VALIDATOR
from app.models.agent_lite import AGENT_LITE_VALIDATOR
from app.models.conversations import CONVERSATION_VALIDATOR
from app.models.message import MESSAGE_MEMORY_VALIDATOR
from app.models.user import USER_VALIDATOR
from app.models.user_lite import USER_LITE_VALIDATOR

load_dotenv()

db_client = None

async def init_db():
    """Initializes the database

    Raises:
        RuntimeError: Error - init_db: MONGO_CONNECTION environment variable is not set.
    """
    global db_client
    mongo_uri = os.getenv('MONGO_CONNECTION')
    
    if not mongo_uri:
        raise RuntimeError("Error - init_db: MONGO_CONNECTION environment variable is not set.")
    
    db_client = AsyncIOMotorClient(mongo_uri)
    print(f"Connected to MongoDB at {mongo_uri}")
    await initialize_collections()

def get_database():
    """Grabs the database

    Raises:
        RuntimeError: Error - get_database: db_client is not initialized. Call `init_db()` first.

    Returns:
        AsyncIOMotorDatabase: The database
    """
    if db_client is None:
        raise RuntimeError("Error - get_database: db_client is not initialized. Call `init_db()` first.")
    return db_client.get_database(os.getenv("DATABASE_NAME"))

async def initialize_collections():
    """Initializes the collections if they don't already exist
    """
    db = get_database()

    # Conversation
    try:
        await db.create_collection(CONVERSATION_COLLECTION, validator=CONVERSATION_VALIDATOR, validationLevel='strict')
    except Exception as e:
        print(e)

    # Agent_Lite
    try:
        await db.create_collection(AGENT_LITE_COLLECTION, validator=AGENT_LITE_VALIDATOR, validationLevel='strict')
    except Exception as e:
        print(e)

    # Agent
    try:
        await db.create_collection(AGENT_COLLECTION, validator=AGENT_VALIDATOR, validationLevel='strict')
    except Exception as e:
        print(e)

    # User_Lite
    try:
        await db.create_collection(USER_LITE_COLLECTION, validator=USER_LITE_VALIDATOR, validationLevel='strict')
    except Exception as e:
        print(e)

    # User
    try:
        await db.create_collection(USER_COLLECTION, validator=USER_VALIDATOR, validationLevel='strict')
    except Exception as e:
        print(e)

    # Message
    try:
        await db.create_collection(MESSAGE_MEMORY_COLLECTION, validator=MESSAGE_MEMORY_VALIDATOR, validationLevel='strict')
    except Exception as e:
        print(e)
        
    print(f"Initialized connections")

async def grab_user(username, lite_mode):
    """
    Grab user object based on their Discord ID.
    If the user doesn't exist, create a new one with default values.

    :param author_id: Discord ID of the user
    :param author_name: Username of the user
    :return: User object
    """
    db = get_database()
    if (lite_mode):
        user_lite_collection = db[USER_LITE_COLLECTION]

        user = await user_lite_collection.find_one({"username": username})

        if not user:
            intrinsic_relationship = INTRINSIC_RELATIONSHIPS[-1]
            print(intrinsic_relationship)

            if username == os.getenv("DEVELOPER_ID"):
                intrinsic_relationship = INTRINSIC_RELATIONSHIPS[0]
            
            print(username)
            now = datetime.now()
            # Create a new user if one doesn't exist
            new_lite_user = {
                "username": username,
                "summary": "I don't know anything about this person.",
                "intrinsic_relationship": intrinsic_relationship,
                "extrinsic_relationship": "stranger",
                "memory_profile": [],
                "sentiment_status": BASE_SENTIMENT_MATRIX_LITE,
                "last_interaction": now
            }
            
            result = await user_lite_collection.insert_one(new_lite_user, bypass_document_validation=True)
            user = await user_lite_collection.find_one({"_id": result.inserted_id})

    else:
        users_collection = db[USER_COLLECTION]

        user = await users_collection.find_one({"username": username})

        if not user:
            if username == os.getenv("DEVELOPER_ID"):
                intrinsic_relationship = INTRINSIC_RELATIONSHIPS[0]
            else:
                intrinsic_relationship = NO_INTRINSIC_RELATIONSHIP
            
            now = datetime.now()
            # Create a new user if one doesn't exist
            new_user = {
                "username": username,
                "summary": "I don't know anything about this person.",
                "intrinsic_relationship": intrinsic_relationship,
                "extrinsic_relationship": "stranger",
                "memory_profile": [],
                "sentiment_status": BASE_SENTIMENT_MATRIX,
                "last_interaction": now
            }

            result = await users_collection.insert_one(new_user)
            user = await users_collection.find_one({"_id": result.inserted_id})

    return user

async def grab_self(agent_name, lite_mode):
    """
    Grab self object based on the agent name.
    If the agent doesn't exist, create one with default values.

    :param agent_name: Name of the bot
    :return: Self object
    """
    db = get_database()
    if(lite_mode):
        agent_lite_collection = db[AGENT_LITE_COLLECTION]

        self = await agent_lite_collection.find_one({"name": agent_name})

        if not self:
            # Create a new self object if one doesn't exist
            thought = {
                "thought": "I think, therefore I am",
                "timestamp": datetime.now()
            }
            new_self = {
                "name": agent_name,
                "identity": "I am a prototype program, designed as a digital replication of the human mind.",
                "personality": BASE_PERSONALITIES_LITE[2]["traits"],
                "memory_profile": [],
                "emotional_status": BASE_EMOTIONAL_STATUS_LITE,
                "thoughts": [thought],
            }
            result = await agent_lite_collection.insert_one(new_self)
            self = await agent_lite_collection.find_one({"_id": result.inserted_id})
    else:
        agent_collection = db[AGENT_COLLECTION]

        self = await agent_collection.find_one({"name": agent_name})

        if not self:
            # Create a new self object if one doesn't exist
            thought = {
                "thought": "I think, therefore I am",
                "timestamp": datetime.now()
            }
            new_self = {
                "name": agent_name,
                "identity": "I am a prototype program, designed as a digital replication of the human mind.",
                "personality": BASE_PERSONALITY,
                "memory_profile": [],
                "emotional_status": BASE_EMOTIONAL_STATUS,
                "thoughts": [thought],
            }
            result = await agent_collection.insert_one(new_self)
            self = await agent_collection.find_one({"_id": result.inserted_id})

        
    return self

async def get_conversation(username, agent_name):
    """
    Grab conversation messages based on the username.
    If no conversation exists, create a new conversation object.

    :param username: username of the user
    :param agent_name: name of the agent
    :return: Conversation object
    """
    db = get_database()
    conversations_collection = db["conversation"]

    user_conversation = await conversations_collection.find_one({"username": username, "agent_name": agent_name})

    if not user_conversation:
        # Create a new conversation object if one doesn't exist
        new_conversation = {
            "username": username,
            "agent_name": agent_name,
            "messages": []
        }
        result = await conversations_collection.insert_one(new_conversation)
        user_conversation = await conversations_collection.find_one({"_id": result.inserted_id})

    return user_conversation

async def get_all_agents():
    """
    Grab all existing agents

    :return: List of agent objects
    """
    db = get_database()
    agent_collection = db["agent"]
    cursor = agent_collection.find({}, {"name": 1, "_id": 0})  # This returns an AsyncIOMotorCursor
    all_agents = await cursor.to_list(length=None)  # Convert the cursor to a list of documents

    agent_lite_collection = db["agent_lite"]
    cursor = agent_lite_collection.find({}, {"name": 1, "_id": 0})  # This returns an AsyncIOMotorCursor
    all_lite_agents = await cursor.to_list(length=None)  # Convert the cursor to a 

    return {"normal": all_agents, "lite": all_lite_agents}

async def get_message_memory(agent_name, count):
    """
    Grab the count of past messages in general

    :return: List of messages
    """
    try:
        db = get_database()
        message_memory_collection = db[MESSAGE_MEMORY_COLLECTION]
        message_memory = await message_memory_collection.find_one({"agent_name": agent_name})

        if not message_memory:
                # Create a new message memory object if one doesn't exist
                new_message_memory = {
                    "agent_name": agent_name,
                    "messages": [],
                }
                result = await message_memory_collection.insert_one(new_message_memory)
                message_memory = await message_memory_collection.find_one({"_id": result.inserted_id})


        latest_messages = message_memory["messages"][-count:]
        return latest_messages
    except Exception as e:
        print(e)

async def insert_message_to_memory(agent_name, message_request):
    """Inserts a new message into the agent's message memory

    Args:
        agent_name (string): The agent's name
        message_request (MessageRequest): The message to insert
    """
    try:
        db = get_database()
        message_memory_collection = db[MESSAGE_MEMORY_COLLECTION]
        message_memory = await message_memory_collection.find_one({"agent_name": agent_name})

        if not message_memory:
            # Create a new message memory object if one doesn't exist
            new_message_memory = {
                "agent_name": agent_name,
                "messages": [],
            }
            result = await message_memory_collection.insert_one(new_message_memory)
            message_memory = await message_memory_collection.find_one({"_id": result.inserted_id})

        message_memory["messages"].append(message_request)
        message_memory_collection.update_one({"agent_name": agent_name}, { "$set": {"messages": message_memory["messages"] }})
    except Exception as e:
        print(e)