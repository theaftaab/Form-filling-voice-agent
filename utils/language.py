# utils/language.py
"""
Language utilities for enforcing script consistency and normalizing STT outputs.
Supports:
  - Force Romanization (ASCII/Latin-only for English)
  - Force Kannada Scripting (native Kannada script for Kannada)
  - General text normalization
"""

import re
from typing import Literal

try:
    # external lib for transliteration (Indic scripts)
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
except ImportError:
    transliterate = None  # fallback if lib not installed


# -------------------------------------------------------------------
# Basic Cleaning
# -------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Trim spaces, normalize multiple spaces, strip weird chars."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# -------------------------------------------------------------------
# Romanization
# -------------------------------------------------------------------

def force_romanization(text: str) -> str:
    """
    Convert input to strict ASCII/Latin characters.
    - Drops diacritics
    - Removes non-ASCII characters
    """
    if not text:
        return ""

    # normalize spacing
    text = clean_text(text)

    # remove all non-ascii
    ascii_text = text.encode("ascii", "ignore").decode("ascii")
    return ascii_text


# -------------------------------------------------------------------
# Kannada Scripting
# -------------------------------------------------------------------

def force_kannada_scripting(text: str) -> str:
    """
    Convert Latin text to Kannada script if possible.
    Uses indic-transliteration if available.
    If not installed, returns text unchanged.
    """
    if not text:
        return ""

    text = clean_text(text)

    if transliterate:
        try:
            return transliterate(text, sanscript.ITRANS, sanscript.KANNADA)
        except Exception:
            # if transliteration fails, return original
            return text
    else:
        # fallback: return as-is
        return text


# -------------------------------------------------------------------
# Normalization Dispatcher
# -------------------------------------------------------------------

def normalize_text(text: str, target_language: Literal["english", "kannada"]) -> str:
    """
    Normalize text based on selected target language.
    - english → force romanization (ASCII)
    - kannada → force Kannada script
    """
    if not text:
        return ""

    if target_language == "english":
        return force_romanization(text)

    if target_language == "kannada":
        return force_kannada_scripting(text)

    # fallback → just clean
    return clean_text(text)


# -------------------------------------------------------------------
# STT Language Updates
# -------------------------------------------------------------------

async def update_stt_language(session, language: str):
    """Update STT language hints based on user's selected language"""
    from livekit.plugins import soniox
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        if language.lower() == "kannada":
            # Focus on Kannada with English fallback for mixed speech
            language_hints = ["kn", "en"]
            context = (
                "Karnataka Government voice assistant in Kannada script. "
                "Form filling: names, addresses, phone numbers, tree species, land measurements. "
                "Common Kannada words: ಹೆಸರು, ವಿಳಾಸ, ಫೋನ್, ಗ್ರಾಮ, ತಾಲೂಕು, ಜಿಲ್ಲೆ, ಮರ, ವಯಸ್ಸು. "
                "Mixed Kannada-English speech allowed."
            )
        else:
            # ULTRA STRICT ENGLISH ONLY - NO OTHER LANGUAGES DETECTED
            language_hints = ["en"]  # ABSOLUTELY ONLY English
            context = (
                "STRICT ENGLISH TRANSCRIPTION ONLY. IGNORE ALL OTHER LANGUAGES. "
                "FORCE ROMANIZE: آفتاب حسین → Aftaab Hussain, محمد خاصم → Mohammed Khasim "
                "DETECT LANGUAGE AS ENGLISH ONLY. DO NOT DETECT URDU, ARABIC, HINDI. "
                "TRANSCRIBE ALL SPEECH AS ENGLISH WORDS IN LATIN SCRIPT. "
                "COMMON INDIAN NAMES IN ENGLISH: Aftaab, Hussain, Mohammed, Khasim, Ahmed, Ali, Khan, Sheikh "
                "WAIT FOR COMPLETE MULTI-WORD NAMES: FirstName LastName pattern. "
                "EXAMPLES: Aftaab Hussain (complete), Mohammed Khasim (complete), Ahmed Ali (complete). "
                "ABSOLUTELY FORBIDDEN: Arabic script آفتاب, Urdu script, Devanagari script. "
                "MANDATORY: A-Z a-z 0-9 spaces only. English government form system. "
                "OVERRIDE LANGUAGE DETECTION - FORCE ENGLISH OUTPUT REGARDLESS OF INPUT LANGUAGE."
            )

        # Create new STT options with updated language settings
        new_soniox_options = soniox.STTOptions(
            language_hints=language_hints,
            context=context,
        )

        # Update the session's STT
        session._stt = soniox.STT(params=new_soniox_options)
        logger.info(f"Updated STT language hints to: {language_hints}")
        
    except Exception as e:
        logger.error(f"Failed to update STT language: {e}")


# -------------------------------------------------------------------
# Example (manual test)
# -------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        "آفتاب حسین",   # Arabic script
        "ಅಫ್ತಾಬ್ ಹುಸೈನ್",  # Kannada script
        "Aftaab Hussain",  # Latin
    ]

    for s in samples:
        print("RAW:", s)
        print(" -> English:", normalize_text(s, "english"))
        print(" -> Kannada:", normalize_text(s, "kannada"))
        print("---")