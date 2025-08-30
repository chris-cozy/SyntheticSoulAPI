from dotenv import load_dotenv
import os


load_dotenv()


API_VERSION = "1.0.0"


BOT_NAME = os.getenv("BOT_NAME")


# CORS
ALLOWED_ORIGINS = [
"http://localhost:5173",
os.getenv("WEB_UI_DOMAIN"),
]


# Redis url (supports plain or TLS)
REDIS_URL = os.getenv("REDIS_TLS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")