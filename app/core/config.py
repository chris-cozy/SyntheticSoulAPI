from dotenv import load_dotenv
import os


load_dotenv()


API_VERSION = "1.0.0"

AGENT_NAME = os.getenv("BOT_NAME")

# OpenAI
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
GPT_FAST = os.getenv('GPT_FAST_MODEL')
GPT_QUALITY = os.getenv('GPT_QUALITY_MODEL')

# Deepseek
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL')

LITE_MODE = os.getenv("MODE") == "lite"

MONGO_CONNECTION = os.getenv('MONGO_CONNECTION')

DEVELOPER_ID = os.getenv("DEVELOPER_ID")

DATABASE_NAME = os.getenv("DATABASE_NAME")

WINDOWS_ENV = os.getenv("ENVIRONMENT") == 'windows'

# CORS
ALLOWED_ORIGINS = [
"http://localhost:5173",
os.getenv("WEB_UI_DOMAIN"),
]

# Redis url (supports plain or TLS)
REDIS_URL = os.getenv("REDIS_TLS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Periodic Rates
EMOTIONAL_DECAY_RATE = 240
THINKING_RATE = 300

# Message Retention
CONVERSATION_MESSAGE_RETENTION_COUNT = 10
MESSAGE_HISTORY_COUNT = 10

# Thought randomizer
RANDOM_THOUGHT_PROBABILITY = 0.4