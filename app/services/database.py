import asyncio
from datetime import datetime
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from app.constants.constants import AGENT_RICH_COLLECTION, AGENT_LITE_COLLECTION, AGENT_NAME_PROPERTY, AUTH_COLLECTION, BASE_EMOTIONAL_STATUS, BASE_EMOTIONAL_STATUS_LITE, BASE_PERSONALITY, BASE_SENTIMENT_MATRIX, BASE_SENTIMENT_MATRIX_LITE, CONVERSATION_COLLECTION, INTRINSIC_RELATIONSHIPS, MEMORY_COLLECTION, MESSAGE_COLLECTION, MYERS_BRIGGS_PERSONALITIES, SESSIONS_COLLECTION, THOUGHT_COLLECTION, USER_RICH_COLLECTION, USER_LITE_COLLECTION, USER_NAME_PROPERTY
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import AGENT_NAME, LITE_MODE, MONGO_CONNECTION, DEVELOPER_EMAIL, DATABASE_NAME

from app.constants.validators import AGENT_RICH_VALIDATOR, AUTH_VALIDATOR, MEMORY_VALIDATOR, MESSAGES_VALIDATOR, SESSIONS_VALIDATOR, THOUGHT_VALIDATOR, USER_RICH_VALIDATOR
from app.constants.validators import AGENT_LITE_VALIDATOR
from app.constants.validators import CONVERSATION_VALIDATOR
from app.constants.validators import USER_LITE_VALIDATOR
from app.domain.agent import ObjectId
from app.domain.memory import Memory

# ---- Globals guarded by a simple init flag
_db_client: AsyncIOMotorClient | None = None
_db_init_done: bool = False

if LITE_MODE:
    AGENT_COLLECTION = AGENT_LITE_COLLECTION
    AGENT_VALIDATOR = AGENT_LITE_VALIDATOR
    
    USER_COLLECTION = USER_LITE_COLLECTION
    USER_VALIDATOR = USER_LITE_VALIDATOR
else:
    AGENT_COLLECTION = AGENT_RICH_COLLECTION
    AGENT_VALIDATOR = AGENT_RICH_VALIDATOR
    
    USER_COLLECTION = USER_RICH_COLLECTION
    USER_VALIDATOR = USER_RICH_VALIDATOR

_VALIDATORS: Dict[str, Dict[str, Any]] = {
    CONVERSATION_COLLECTION: CONVERSATION_VALIDATOR,
    AGENT_COLLECTION:        AGENT_VALIDATOR,
    USER_COLLECTION:    USER_VALIDATOR,
    MEMORY_COLLECTION: MEMORY_VALIDATOR,
    MESSAGE_COLLECTION: MESSAGES_VALIDATOR,
    THOUGHT_COLLECTION: THOUGHT_VALIDATOR,
    SESSIONS_COLLECTION: SESSIONS_VALIDATOR,
    AUTH_COLLECTION: AUTH_VALIDATOR
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
    await db[AGENT_COLLECTION].create_index("name", unique=True)
    
    await db[AUTH_COLLECTION].create_index("email", unique=True, sparse=True, name="email_unique")
    await db[AUTH_COLLECTION].create_index("_id", unique=False, name="user_id")
    
    await db[USER_COLLECTION].create_index(
        [("user_id", 1), ("agent_perspective", 1)],
        unique=True,
        sparse=True,             # so old docs without user_id don't conflict
        name="user_id_agent_perspective"
    )
    
    await db[CONVERSATION_COLLECTION].create_index(
        [("user_id", 1), ("agent_name", 1)],
        name="user_id_agent"
    )
    await db[MESSAGE_COLLECTION].create_index("sender", name="sender")
    
    await db[MEMORY_COLLECTION].create_index(
        [("agent_name", 1), ("ts_created", -1)],
        name="agent_time"
    )
    await db[MEMORY_COLLECTION].create_index("tags", name="tags")
    await db[MEMORY_COLLECTION].create_index("recall_count", name="recalls")
    
    await db[THOUGHT_COLLECTION].create_index("agent_name", name="agent_name")
    
    # Sessions
    await db[SESSIONS_COLLECTION].create_index("_id", name="sid_unique")
    await db[SESSIONS_COLLECTION].create_index([("user_id", 1), ("revoked", 1)], name="user_revoked")
    await db[SESSIONS_COLLECTION].create_index("expires_at", expireAfterSeconds=0, name="expires_ttl")

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
    
    mongo_uri = MONGO_CONNECTION
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
    '''
    print(
        "DB init timings (s): "
        + ", ".join(f"{k}={v:.3f}" for k, v in timings.items())
    )
    '''
    
def _get_db_name() -> str:
    name = DATABASE_NAME
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
    
    '''
    print(
        "Collection init: "
        f"list_names={list_names_time:.3f}s, "
        f"created={len(to_create)} in {create_time:.3f}s, "
        f"validated={len(to_update_validator)} in {update_time:.3f}s"
    )
    '''

async def grab_user(user_id):
    """
    Grab user object based on their Discord ID.
    If the user doesn't exist, create a new one with default values.

    :param username: Username of the user
    :return: User object
    """
    db = await get_database()
    
    if LITE_MODE:
        user_collection = db[USER_LITE_COLLECTION]
    else:
        user_collection = db[USER_RICH_COLLECTION]
        
    if user_id:
        doc = await db[user_collection].find_one({"user_id": user_id, "agent_perspective": AGENT_NAME})
        if doc: return doc
    return None

async def grab_self():
    """
    Grab self object based on the agent name.
    If the agent doesn't exist, create one with default values.

    :param agent_name: Name of the bot
    :return: Self object
    """
    db = await get_database()
    
    now = datetime.now()
    if LITE_MODE:
        agent_collection = db[AGENT_LITE_COLLECTION]
        default_personality = random.choice(MYERS_BRIGGS_PERSONALITIES)
        default_emotional_status = BASE_EMOTIONAL_STATUS_LITE
    else:
        agent_collection = db[AGENT_RICH_COLLECTION]
        default_personality = BASE_PERSONALITY
        default_emotional_status = BASE_EMOTIONAL_STATUS
    
    self = await agent_collection.find_one({"name": AGENT_NAME})

    if not self:
        result = await agent_collection.insert_one({
            "name": AGENT_NAME,
            "identity": f"I am a program designed to simulate human-like thought processes and logical reasoning. I was born on {datetime.now()}",
            "personality": default_personality,
            "memory_tags": [],
            "emotional_status": default_emotional_status,
            "birthdate": now
        })
        self = await agent_collection.find_one({"_id": result.inserted_id})
            
    return self

async def get_conversation(user_id, agent_name=AGENT_NAME):
    """
    Grab conversation messages based on the username.
    If no conversation exists, create a new conversation object.

    :param username: username of the user
    :param agent_name: name of the agent
    :return: Conversation object
    """
    db = await get_database()
    conversations_collection = db[CONVERSATION_COLLECTION]

    user_conversation = await conversations_collection.find_one({"user_id": user_id, "agent_name": agent_name})

    if not user_conversation:
        # Create a new conversation object if one doesn't exist
        new_conversation = {
            "user_id": user_id,
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
    agent_collection = db[AGENT_RICH_COLLECTION]
    cursor = agent_collection.find({}, {"name": 1, "_id": 0})  # This returns an AsyncIOMotorCursor
    all_agents = await cursor.to_list(length=None)  # Convert the cursor to a list of documents

    agent_lite_collection = db["agent_lite"]
    cursor = agent_lite_collection.find({}, {"name": 1, "_id": 0})  # This returns an AsyncIOMotorCursor
    all_lite_agents = await cursor.to_list(length=None)  # Convert the cursor to a 

    return {"normal": all_agents, "lite": all_lite_agents}
        
async def get_all_message_memory(count, agent_name=AGENT_NAME):
    """
    Grab the count of past messages in general

    :return: List of messages
    """
    try:
        db = await get_database()
        message_collection = db[MESSAGE_COLLECTION]
        
        cursor = (
            message_collection
            .find({"sender": agent_name})
            .sort([("_id", -1)])   # Sort descending by _id (newest first)
            .limit(count)
        )
        
        latest_messages = await cursor.to_list(length=count)
        return latest_messages
    except Exception as e:
        print(e)
        return []
    
async def get_tagged_memories(
    tag: str,
    limit: int = 100,
    before_id: Optional[str] = None
    )->List[dict[str, Any]]:
    """
    Grab memories related to the tag

    :return: List of memories
    """
    try:
        db = await get_database()
        memory_collection = db[MEMORY_COLLECTION]
        
        query: dict[str, Any] = {"tags": tag}
        if before_id:
            query["_id"] = {"$lt": ObjectId(before_id)}
            
        cursor = (
            memory_collection
            .find(query)
            .sort([("_id", -1)])   # Sort descending by _id (newest first)
            .limit(limit)
        )
        
        related_memories = await cursor.to_list(length=limit)
        return related_memories
    except Exception as e:
        print(e)
        return []
        
async def insert_message_to_conversation(
    user_id: str,
    message: dict[str, Any],
    agent_name: str =AGENT_NAME,
) -> None:
    try:
        db = await get_database()
        conversation_collection = db[CONVERSATION_COLLECTION]
        await conversation_collection.update_one(
            {"user_id": user_id, "agent_name": agent_name}, 
            { 
            "$push": 
                {
                    "messages": {
                        "$each": [message],
                        "$slice": -1000 
                        }
                    },
                "$setOnInsert": {"user_id": user_id, "agent_name": agent_name}
            },
            upsert=True
        )
    except Exception as e:
        print(e)

async def insert_message_to_message_memory(
    message: dict[str, Any]
) -> None:
    try:
        db = await get_database()
        messsage_collection = db[MESSAGE_COLLECTION]
        message["agent"] = AGENT_NAME
        await messsage_collection.insert_one(message)
    except Exception as e:
        print(e)
        
async def add_thought(
    thought: dict[str, Any],
    agent_name: str=AGENT_NAME,
) -> None:
    try:
        db = await get_database()
        thought_collection = db[THOUGHT_COLLECTION]
        
        thought["agent_name"] = agent_name
        
        await thought_collection.insert_one(thought)
    except Exception as e:
        print(e)
        
async def get_thoughts(
    count,
    agent_name: str=AGENT_NAME,
) -> None:
    try:
        db = await get_database()
        thought_collection = db[THOUGHT_COLLECTION]
        
        cursor = (
            thought_collection
            .find({"agent_name": agent_name})
            .sort([("_id", -1)])   # Sort descending by _id (newest first)
            .limit(count)
        )
        
        latest_thoughts = await cursor.to_list(length=count)
        return latest_thoughts
    except Exception as e:
        print(e)
               
async def add_memory(mem: Memory):
    try:
        db = await get_database()
        memory_collection = db[MEMORY_COLLECTION]
        doc = mem.model_dump()
        await memory_collection.insert_one(doc)
    except Exception as e:
        print(e)
        
async def update_tags(new_tags: List[str]):
    try:
        db = await get_database()
        agent_lite_collection = db[AGENT_LITE_COLLECTION]
        await agent_lite_collection.update_one(
            {AGENT_NAME_PROPERTY: AGENT_NAME},
            {"$addToSet": {"memory_tags": {"$each": new_tags}}}
        )
    except Exception as e:
        print(e)
      
async def update_summary_identity_relationship(user_id, summary, extrinsic_relationship, identity, agent_name=AGENT_NAME):
    """Updates the user summary, agent identity, and user extrinsic relationship

    Args:
        agent_name (string): The agent's name
        user_id (string): The user's ID
        summary (string): The updated summary
        extrinsic_relationship (string): The updated extrinsic relationship
        identity (string): The updated identity
    """
    try:
        db = await get_database()
        if LITE_MODE:
            agent_collection = db[AGENT_LITE_COLLECTION]
            user_collection = db[USER_LITE_COLLECTION]

        agent_collection.update_one({'name': agent_name}, {"$set": {"identity": identity}})
        user_collection.update_one({"user_id": user_id, "agent_perspective": agent_name}, {"$set": {"summary": summary, "extrinsic_relationship": extrinsic_relationship}})
    except Exception as e:
        print(e)
        
async def update_agent_emotions(emotions, agent_name=AGENT_NAME):
    try:
        db = await get_database()
        if LITE_MODE:
            agent_collection = db[AGENT_LITE_COLLECTION]
        
        agent_collection.update_one({AGENT_NAME_PROPERTY: agent_name}, { "$set": {"emotional_status": emotions }})
    
    except Exception as e:
        print(e)
        
async def update_user_sentiment(user_id, sentiments):
    try:
        db = await get_database()
        if LITE_MODE:
            user_collection = db[USER_LITE_COLLECTION]
        
        user_collection.update_one({"user_id": user_id}, { "$set": { "sentiment_status": sentiments, "last_interaction": datetime.now() }})
    except Exception as e:
        print(e)
        
async def ensure_user_and_profile(user_id: str, username: str, agent_name: str = AGENT_NAME):
    """
    idempotent: ensure 'users' identity + 'user_lite' perspective doc
    """
    db = await get_database()
    now = datetime.now()

    # 1) identity (users)
    await db[AUTH_COLLECTION].update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "_id": user_id,
                "username": username,
                "created_at": now,
                "auth": {"type": "guest"},
                "roles": ["user"],
            }
        },
        upsert=True,
    )

    # 2) perspective (user_lite)
    default_intrinsic_relationship = INTRINSIC_RELATIONSHIPS[-1]
    
    if LITE_MODE:
        user_collection = db[USER_LITE_COLLECTION]
        default_sentiments = BASE_SENTIMENT_MATRIX_LITE
    else:
        user_collection = db[USER_RICH_COLLECTION]
        default_sentiments = BASE_SENTIMENT_MATRIX

    doc = await user_collection.find_one({"user_id": user_id, "agent_perspective": agent_name})
    if not doc:
        new_user_lite = {
            "user_id": user_id,
            "username": username,           # keep for compat / display
            "agent_perspective": agent_name,
            "summary": "I don't know anything about this person.",
            "intrinsic_relationship": default_intrinsic_relationship,
            "extrinsic_relationship": "stranger",
            "sentiment_status": default_sentiments,
            "last_interaction": now,
        }
        await user_collection.insert_one(new_user_lite)
        doc = new_user_lite

    return doc
        
        
