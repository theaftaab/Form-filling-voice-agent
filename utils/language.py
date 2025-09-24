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