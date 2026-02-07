from dotenv import load_dotenv
import os

load_dotenv()

API_VERSION = "1.1.0"
_version_parts = API_VERSION.split(".")
if len(_version_parts) != 3 or not all(p.isdigit() for p in _version_parts):
    raise RuntimeError(f"API_VERSION must be semver 'MAJOR.MINOR.PATCH', got: {API_VERSION}")

API_MAJOR_VERSION = int(_version_parts[0])
API_MINOR_VERSION = int(_version_parts[1])
API_PATCH_VERSION = int(_version_parts[2])
API_BASE_PATH = f"/v{API_MAJOR_VERSION}"

AGENT_NAME = os.getenv("BOT_NAME", "jasmine")
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()

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

DEVELOPER_EMAIL = os.getenv("DEVELOPER_EMAIL")

DATABASE_NAME = os.getenv("DATABASE_NAME")

WINDOWS_ENV = os.getenv("ENVIRONMENT") == 'windows'

# Optional Argon2 pepper (extra secret in env)
ARGON2_PEPPER_ENV = os.getenv("ARGON2_PEPPER_ENV", "dev-change-me")

JWT_SECRET_ENV = os.getenv("JWT_SECRET_ENV", "dev-change-me")

# Token TTLs (env override)
ACCESS_TTL_MIN_DEFAULT = 15
REFRESH_TTL_DAYS_DEFAULT = 90

ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", ACCESS_TTL_MIN_DEFAULT))

REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", REFRESH_TTL_DAYS_DEFAULT))

# CORS
_raw_allowed_origins = [
    "http://localhost:5173",
    os.getenv("WEB_UI_DOMAIN"),
]
ALLOWED_ORIGINS = [origin.rstrip("/") for origin in _raw_allowed_origins if origin]
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin.startswith(("http://", "https://"))]

# Redis url (supports plain or TLS)
REDIS_URL = os.getenv("REDIS_TLS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CA_CERT = os.getenv("REDIS_CA_CERT")
REDIS_TLS_INSECURE_SKIP_VERIFY = os.getenv("REDIS_TLS_INSECURE_SKIP_VERIFY", "false").strip().lower() in {"1", "true", "yes", "on"}

# Periodic Rates
EMOTIONAL_DECAY_RATE = int(os.getenv("EMOTIONAL_DECAY_RATE_SECONDS", 240))
THINKING_RATE = int(os.getenv("THINKING_RATE_SECONDS", 900))

# Message Retention
CONVERSATION_MESSAGE_RETENTION_COUNT = 10
MESSAGE_HISTORY_COUNT = 10

# Thought randomizer
RANDOM_THOUGHT_PROBABILITY = 0.4


EXPRESSIONS_DIR = os.getenv("EXPRESSIONS_DIR") or os.path.join(os.path.dirname(__file__), "..", "assets", "expressions", AGENT_NAME.lower())

_ALLOWED_EXPRESSIONS_EXTS = {".jpeg", ".webp", ".gif", ".png", ".jpg"}

DEBUG_MODE = os.getenv("DEBUG_MODE", "true").strip().lower() in {"1", "true", "yes", "on"}


def validate_security_configuration() -> None:
    is_dev = APP_ENV in {"dev", "development", "local", "test"}
    if is_dev:
        return

    if JWT_SECRET_ENV == "dev-change-me":
        raise RuntimeError("JWT_SECRET_ENV must be set to a secure random value in non-dev environments.")
    if ARGON2_PEPPER_ENV == "dev-change-me":
        raise RuntimeError("ARGON2_PEPPER_ENV must be set to a secure random value in non-dev environments.")

    if len(JWT_SECRET_ENV) < 32:
        raise RuntimeError("JWT_SECRET_ENV must be at least 32 characters in non-dev environments.")
    if len(ARGON2_PEPPER_ENV) < 16:
        raise RuntimeError("ARGON2_PEPPER_ENV must be at least 16 characters in non-dev environments.")
    if REDIS_TLS_INSECURE_SKIP_VERIFY:
        raise RuntimeError("REDIS_TLS_INSECURE_SKIP_VERIFY cannot be enabled in non-dev environments.")
