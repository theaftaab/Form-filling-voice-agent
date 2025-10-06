import os
import logging
from dotenv import load_dotenv
from livekit.plugins import openai, soniox, elevenlabs, groq

print("Loading .env file...")
load_dotenv()
print(".env loaded successfully")

# ------------------------------------------------------
# Environment Variables
# ------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SONIOX_API_KEY = os.getenv("SONIOX_API_KEY")

SSL_CERT_FILE = os.getenv("SSL_CERT_FILE")
DISABLE_SSL_VERIFY = os.getenv("DISABLE_SSL_VERIFY", "false").lower() == "true"

# ------------------------------------------------------
# ElevenLabs Configuration
# ------------------------------------------------------

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # ✅ unified name
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")  # from voices list
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

# ------------------------------------------------------
# Defaults
# ------------------------------------------------------

DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
TEST_LLM_MODEL = os.getenv("TEST_LLM_MODEL", "gpt-4o-mini")
SUPPORTED_LANGUAGES = ["english", "kannada"]

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ------------------------------------------------------
# Default Plugins (LLM, STT, TTS)
# ------------------------------------------------------

DEFAULT_LLM = openai.LLM(model=DEFAULT_LLM_MODEL,temperature=0)
TEST_LLM = groq.LLM(model=TEST_LLM_MODEL,temperature=0)

DEFAULT_STT = soniox.STT(
    params=soniox.STTOptions(
        language_hints=["en", "kn"],
        context="Karnataka Government voice assistant..."
    )
)

DEFAULT_TTS = openai.TTS(
    voice="alloy",  # voices: "alloy", "verse", "soft", "bright", etc.
    model="gpt-4o-mini-tts"
)

# ------------------------------------------------------
# Logger Setup
# ------------------------------------------------------

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
    logger = logging.getLogger("gov-assistant")
    logger.setLevel(logging.INFO)


def is_production() -> bool:
    return os.getenv("ENV", "development").lower() == "production"