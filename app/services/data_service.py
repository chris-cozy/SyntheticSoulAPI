import asyncio
from datetime import datetime
import os
import time
from typing import Any, Dict, List, Tuple
from app.constants.constants import AGENT_COLLECTION, AGENT_LITE_COLLECTION, AGENT_NAME_PROPERTY, BASE_EMOTIONAL_STATUS, BASE_EMOTIONAL_STATUS_LITE, BASE_PERSONALITIES_LITE, BASE_PERSONALITY, BASE_SENTIMENT_MATRIX, BASE_SENTIMENT_MATRIX_LITE, CONVERSATION_COLLECTION, INTRINSIC_RELATIONSHIPS, MESSAGE_MEMORY_COLLECTION, USER_COLLECTION, USER_LITE_COLLECTION, USER_NAME_PROPERTY
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.agent import AGENT_VALIDATOR
from app.models.agent_lite import AGENT_LITE_VALIDATOR
from app.models.conversations import CONVERSATION_VALIDATOR
from app.models.message import MESSAGE_MEMORY_VALIDATOR
from app.models.user import USER_VALIDATOR
from app.models.user_lite import USER_LITE_VALIDATOR

load_dotenv()

# ---- Globals guarded by a simple init flag
_db_client: AsyncIOMotorClient | None = None
_db_init_done: bool = False

_VALIDATORS: Dict[str, Dict[str, Any]] = {
    CONVERSATION_COLLECTION: CONVERSATION_VALIDATOR,
    AGENT_LITE_COLLECTION:   AGENT_LITE_VALIDATOR,
    AGENT_COLLECTION:        AGENT_VALIDATOR,
    USER_LITE_COLLECTION:    USER_LITE_VALIDATOR,
    USER_COLLECTION:         USER_VALIDATOR,
    MESSAGE_MEMORY_COLLECTION: MESSAGE_MEMORY_VALIDATOR,
}

def _client_opts() -> Dict[str, Any]:
    # Trim excessive default timeouts; adjust to your infra as needed
    return {
        "serverSelectionTimeoutMS": 5000,  # 5s to pick a server
        "connectTimeoutMS": 5000,          # 5s TCP connect
        "socketTimeoutMS": 10000,          # 10s socket ops
        "uuidRepresentation": "standard",
        # "tls": True, "tlsAllowInvalidCertificates": False,  # if applicable
    }

async def _ensure_indexes(db):
    await db[AGENT_LITE_COLLECTION].create_index("name", unique=True)
    await db[AGENT_COLLECTION].create_index("name", unique=True)
    await db[USER_LITE_COLLECTION].create_index(
        [("username", 1), ("agent_perspective", 1)],
        unique=True,
        name="username_agent_perspective"
    )
    await db[USER_COLLECTION].create_index("username", unique=True)
    await db[CONVERSATION_COLLECTION].create_index(
        [("username", 1), ("agent_name", 1)],
        name="username_agent"
    )
    await db[MESSAGE_MEMORY_COLLECTION].create_index("agent_name", name="agent_name")

db_client = None

async def init_db() -> None:
    """
    Initialize the global Mongo client and collections once.
    Safe to call multiple times; only the first call does work.
    """
    global _db_client, _db_init_done
    
    if _db_init_done and _db_client is not None:
        return
    
    timings: Dict[str, float] = {}
    t0 = time.perf_counter()
    
    mongo_uri = os.getenv('MONGO_CONNECTION')
    if not mongo_uri:
        raise RuntimeError("Error - init_db: MONGO_CONNECTION environment variable is not set.")
    
    # Create client (lazy connect)
    t = time.perf_counter()
    _db_client = AsyncIOMotorClient(mongo_uri)
    timings["client_create"] = time.perf_counter() - t
    
    # Force a quick ping so we fail fast instead of later
    t = time.perf_counter()
    await _db_client.admin.command("ping")
    timings["client_ping"] = time.perf_counter() - t
    
    # Initialize collections (cheap if already present)
    t = time.perf_counter()
    await _initialize_collections(_db_client)
    timings["initialize_collections"] = time.perf_counter() - t
    
    _db_init_done = True
    timings["total_init_db"] = time.perf_counter() - t0
    
    # One-line timing summary
    print(
        "DB init timings (s): "
        + ", ".join(f"{k}={v:.3f}" for k, v in timings.items())
    )
    
def _get_db_name() -> str:
    name = os.getenv("DATABASE_NAME")
    if not name:
        raise RuntimeError("Error - get_database: DATABASE_NAME is not set.")
    return name

async def get_database():
    """
    Returns the DB instance. Ensures init has happened.
    """
    await init_db()
    assert _db_client is not None
    return _db_client.get_database(_get_db_name())

async def _initialize_collections(client: AsyncIOMotorClient) -> None:
    """
    Creates any missing collections and applies validators with minimal overhead.
    Might need to remove asyncio if doesn't function properly on task
    """
    db = client.get_database(_get_db_name())
    
    # 1) Fetch once, avoid per-collection “create then fail” round-trips
    t = time.perf_counter()
    existing = await db.list_collection_names()
    list_names_time = time.perf_counter() - t
    
    # 2) Decide work
    to_create: List[Tuple[str, Dict[str, Any]]] = []
    to_update_validator: List[Tuple[str, Dict[str, Any]]] = []
    
    for coll, validator in _VALIDATORS.items():
        if coll in existing:
            # Optional: ensure validator/validationLevel is in place via collMod
            to_update_validator.append((coll, validator))
        else:
            to_create.append((coll, validator))
            
    # 3) Create missing collections in parallel
    async def _create_one(name: str, validator: Dict[str, Any]) -> None:
        await db.create_collection(name, validator=validator, validationLevel="strict")
        
    # 4) Update validators on existing collections (fast no-op if already set)
    async def _ensure_validator(name: str, validator: Dict[str, Any]) -> None:
        # collMod sets/updates existing options; cheap if already matching
        try:
            await db.command({
                "collMod": name,
                "validator": validator,
                "validationLevel": "strict"
            })
        except Exception as e:
            # Some deployments may not permit collMod; log once, continue
            print(f"collMod skipped for '{name}': {e}")
    
    # Run tasks concurrently but keep them bounded
    create_tasks = [asyncio.create_task(_create_one(n, v)) for n, v in to_create]
    update_tasks = [asyncio.create_task(_ensure_validator(n, v)) for n, v in to_update_validator]
    
    t_create = time.perf_counter()
    if create_tasks:
        await asyncio.gather(*create_tasks)
    create_time = time.perf_counter() - t_create

    t_update = time.perf_counter()
    if update_tasks:
        await asyncio.gather(*update_tasks)
    update_time = time.perf_counter() - t_update
    
    await _ensure_indexes(db)
    
    print(
        "Collection init: "
        f"list_names={list_names_time:.3f}s, "
        f"created={len(to_create)} in {create_time:.3f}s, "
        f"validated={len(to_update_validator)} in {update_time:.3f}s"
    )

async def grab_user(username, agent_name, lite_mode=True):
    """
    Grab user object based on their Discord ID.
    If the user doesn't exist, create a new one with default values.

    :param author_id: Discord ID of the user
    :param author_name: Username of the user
    :return: User object
    """
    db = await get_database()
    if (lite_mode):
        user_lite_collection = db[USER_LITE_COLLECTION]

        user = await user_lite_collection.find_one({"username": username, "agent_perspective": agent_name})

        if not user:
            intrinsic_relationship = INTRINSIC_RELATIONSHIPS[-1]

            if username == os.getenv("DEVELOPER_ID"):
                intrinsic_relationship = INTRINSIC_RELATIONSHIPS[0]
            
            print(username)
            now = datetime.now()
            # Create a new user if one doesn't exist
            new_lite_user = {
                "username": username,
                "agent_perspective": agent_name,
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
                intrinsic_relationship = INTRINSIC_RELATIONSHIPS[-1]
            
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

async def grab_self(agent_name, lite_mode=True):
    """
    Grab self object based on the agent name.
    If the agent doesn't exist, create one with default values.

    :param agent_name: Name of the bot
    :return: Self object
    """
    timings: Dict[str, float] = {}
    t = time.perf_counter()
    db = await get_database()
    timings["self_get_database"] = time.perf_counter() - t
    if(lite_mode):
        t = time.perf_counter()
        agent_lite_collection = db[AGENT_LITE_COLLECTION]

        self = await agent_lite_collection.find_one({"name": agent_name})
        timings["self_find_agent"] = time.perf_counter() - t

        if not self:
            t = time.perf_counter()
            # Create a new self object if one doesn't exist
            thought = {
                "thought": "I think, therefore I am.",
                "timestamp": datetime.now()
            }
            new_self = {
                "name": agent_name,
                "identity": f"I am a program designed to simulate human-like thought processes and logical reasoning. I was born on {datetime.now()}",
                "personality": BASE_PERSONALITIES_LITE[1]["traits"],
                "memory_profile": {"all_tags": [], "memories": []},
                "emotional_status": BASE_EMOTIONAL_STATUS_LITE,
                "thoughts": [thought],
                "birthdate": datetime.now()
            }
            result = await agent_lite_collection.insert_one(new_self)
            self = await agent_lite_collection.find_one({"_id": result.inserted_id})
            timings["self_create_agent"] = time.perf_counter() - t
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

    print(
        "Self init timings (s): "
        + ", ".join(f"{k}={v:.3f}" for k, v in timings.items())
    )
    return self

async def get_conversation(username, agent_name):
    """
    Grab conversation messages based on the username.
    If no conversation exists, create a new conversation object.

    :param username: username of the user
    :param agent_name: name of the agent
    :return: Conversation object
    """
    db = await get_database()
    conversations_collection = db[CONVERSATION_COLLECTION]

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
    agent_collection = db[AGENT_COLLECTION]
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
        db = await get_database()
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
        db = await get_database()
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
        
async def insert_message_to_conversation(
    username: str,
    agent_name: str,
    message: dict[str, Any]
) -> None:
    try:
        db = await get_database()
        conversation_collection = db[CONVERSATION_COLLECTION]
        await conversation_collection.update_one(
        {USER_NAME_PROPERTY: username, "agent_name": agent_name}, 
        { "$push": {"messages": message }})
    except Exception as e:
        print(e)
        
async def add_thought(
    agent_name: str,
    thought: dict[str, Any]
) -> None:
    try:
        db = await get_database()
        thought_collection = db[AGENT_LITE_COLLECTION]
        await thought_collection.update_one({AGENT_NAME_PROPERTY: agent_name}, { "$push": {"thoughts": thought}})
    except Exception as e:
        print(e)
               
async def insert_agent_memory(agent_name, event, thoughts, significance, emotional_impact, tags, lite_mode=True):
    """Inserts a new general memory

    Args:
        agent_name (string): The agent's name
        event (string): The message to insert
        thoughts (string): The agent's name
        significance (string): The significance of the memory. enum (Low, Medium, High)
        emotional_impact (object): The affect this had on the agent's emotions
        tags (array): Array of string tags
    """
    try:
        db = await get_database()
        if(lite_mode):
            agent_lite_collection = db[AGENT_LITE_COLLECTION]

            self = await agent_lite_collection.find_one({"name": agent_name})
            
            all_tags = self['memory_profile']['all_tags']
            memories = self['memory_profile']['memories']
            
            print(tags)
            for tag in tags:
                if tag not in all_tags:
                    all_tags.append(tag)
            
            print(all_tags)
            new_memory = {
                "event": event,
                "thoughts": thoughts,
                "significance": significance,
                "emotional_impact": emotional_impact,
                "tags": tags,
                "timestamp": datetime.now()
            }
            
            memories.append(new_memory)
            
            updated_memory_profile = {
                "all_tags": all_tags,
                "memories": memories
            }
            agent_lite_collection.update_one({'name': agent_name}, {"$set": {"memory_profile": updated_memory_profile}})
    except Exception as e:
        print(e)
        
async def update_summary_identity_relationship(agent_name, username, summary, extrinsic_relationship, identity, lite_mode=True):
    """Updates the user summary, agent identity, and user extrinsic relationship

    Args:
        agent_name (string): The agent's name
        username (string): The user's name
        summary (string): The updated summary
        extrinsic_relationship (string): The updated extrinsic relationship
        identity (string): The updated identity
    """
    try:
        db = await get_database()
        if(lite_mode):
            agent_lite_collection = db[AGENT_LITE_COLLECTION]
            user_lite_collection = db[USER_LITE_COLLECTION]

            agent_lite_collection.update_one({'name': agent_name}, {"$set": {"identity": identity}})
            user_lite_collection.update_one({"username": username, "agent_perspective": agent_name}, {"$set": {"summary": summary, "extrinsic_relationship": extrinsic_relationship}})
    except Exception as e:
        print(e)
        
async def update_agent_emotions(agent_name, emotions, lite_mode=True):
    try:
        db = await get_database()
        if(lite_mode):
            agent_lite_collection = db[AGENT_LITE_COLLECTION]
            agent_lite_collection.update_one({AGENT_NAME_PROPERTY: agent_name}, { "$set": {"emotional_status": emotions }})
    
    except Exception as e:
        print(e)
        
async def update_user_sentiment(username, sentiments, lite_mode=True):
    try:
        db = await get_database()
        if(lite_mode):
            user_lite_collection = db[USER_LITE_COLLECTION]
            user_lite_collection.update_one({USER_NAME_PROPERTY: username}, { "$set": { "sentiment_status": sentiments, "last_interaction": datetime.now() }}, bypass_document_validation=True)
    except Exception as e:
        print(e)
        
        
