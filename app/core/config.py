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

# LLM provider mode
LLM_MODE = os.getenv("LLM_MODE", "hosted").strip().lower()
if LLM_MODE not in {"hosted", "local"}:
    raise RuntimeError("LLM_MODE must be either 'hosted' or 'local'.")

# Ollama (OpenAI-compatible API)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
OLLAMA_FAST_MODEL = os.getenv("OLLAMA_FAST_MODEL")
OLLAMA_QUALITY_MODEL = os.getenv("OLLAMA_QUALITY_MODEL")

LITE_MODE = os.getenv("MODE") == "lite"

# Mongo runtime mode
MONGO_MODE = os.getenv("MONGO_MODE", "hosted").strip().lower()
if MONGO_MODE not in {"hosted", "local"}:
    raise RuntimeError("MONGO_MODE must be either 'hosted' or 'local'.")

# Legacy single-URI fallback remains supported.
MONGO_CONNECTION = os.getenv("MONGO_CONNECTION")
MONGO_CONNECTION_HOSTED = os.getenv("MONGO_CONNECTION_HOSTED")
MONGO_CONNECTION_LOCAL = os.getenv("MONGO_CONNECTION_LOCAL", "mongodb://127.0.0.1:27017")

if MONGO_MODE == "local":
    MONGO_CONNECTION = MONGO_CONNECTION_LOCAL or MONGO_CONNECTION
else:
    MONGO_CONNECTION = MONGO_CONNECTION_HOSTED or MONGO_CONNECTION

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


def validate_llm_configuration() -> None:
    if LLM_MODE == "local":
        missing = [
            key
            for key, value in (
                ("OLLAMA_FAST_MODEL", OLLAMA_FAST_MODEL),
                ("OLLAMA_QUALITY_MODEL", OLLAMA_QUALITY_MODEL),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required local LLM config: {', '.join(missing)}")
        return

    missing = [
        key
        for key, value in (
            ("OPENAI_API_KEY", OPENAI_KEY),
            ("GPT_FAST_MODEL", GPT_FAST),
            ("GPT_QUALITY_MODEL", GPT_QUALITY),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required hosted LLM config: {', '.join(missing)}")


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
