import os
import logging
from dotenv import load_dotenv

print("Loading .env file...")
load_dotenv()
print(".env loaded successfully")

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SONIOX_API_KEY = os.getenv("SONIOX_API_KEY")

SSL_CERT_FILE = os.getenv("SSL_CERT_FILE")
DISABLE_SSL_VERIFY = os.getenv("DISABLE_SSL_VERIFY", "false").lower() == "true"


DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
DEFAULT_TTS_VOICE = os.getenv("DEFAULT_TTS_VOICE", "alloy")

SUPPORTED_LANGUAGES = ["english", "kannada"]

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


# Setup logger
try:
    logger = logging.getLogger("gov-assistant")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
except Exception as e:
    # Fallback logger
    logger = logging.getLogger("gov-assistant")
    logger.setLevel(logging.INFO)


def is_production() -> bool:
    return os.getenv("ENV", "development").lower() == "production"