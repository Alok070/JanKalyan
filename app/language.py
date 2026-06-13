"""
Language detection & localization utilities.

Strategy:
1. Script-based detection (fastest, no API call)
   - Devanagari range → Hindi
   - Tamil range → Tamil
   - Latin → English
2. langdetect as backup
3. Utilities for localized field access
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
#  Unicode script ranges
# ═══════════════════════════════════════════════════════════════════════════
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")


def detect_language(text: str) -> str:
    """
    Detect the dominant language of the input text.
    Returns: 'hi', 'ta', or 'en'
    """
    if not text or not text.strip():
        return "en"

    devanagari_count = len(DEVANAGARI_RE.findall(text))
    tamil_count = len(TAMIL_RE.findall(text))
    total_alpha = sum(1 for c in text if c.isalpha())

    if total_alpha == 0:
        return "en"

    # If > 20% of characters are Devanagari → Hindi
    if devanagari_count / total_alpha > 0.2:
        return "hi"
    # If > 20% of characters are Tamil → Tamil
    if tamil_count / total_alpha > 0.2:
        return "ta"

    # Fallback: try langdetect
    try:
        from langdetect import detect
        detected = detect(text)
        if detected in ("hi", "ta"):
            return detected
    except Exception:
        pass

    return "en"


def is_code_mixed(text: str) -> bool:
    """Check if the text contains mixed scripts (e.g. Hindi + English)."""
    has_devanagari = bool(DEVANAGARI_RE.search(text))
    has_tamil = bool(TAMIL_RE.search(text))
    has_latin = bool(re.search(r"[a-zA-Z]", text))

    scripts = sum([has_devanagari, has_tamil, has_latin])
    return scripts >= 2


# ═══════════════════════════════════════════════════════════════════════════
#  Language name mappings
# ═══════════════════════════════════════════════════════════════════════════
LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
}

SARVAM_LANG_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
}


# ═══════════════════════════════════════════════════════════════════════════
#  Get localized field from a scheme
# ═══════════════════════════════════════════════════════════════════════════

def get_localized(obj, field_base: str, lang: str) -> str:
    """Get the localized version of a field, e.g. 'name' → name_hi."""
    localized_field = f"{field_base}_{lang}"
    fallback_field = f"{field_base}_en"

    if hasattr(obj, localized_field):
        val = getattr(obj, localized_field)
        if val:
            return val

    if hasattr(obj, fallback_field):
        return getattr(obj, fallback_field, "")

    return ""


def get_localized_list(obj, field_base: str, lang: str) -> list[str]:
    """Get the localized list field, e.g. 'documents' → documents_hi."""
    localized_field = f"{field_base}_{lang}"
    fallback_field = f"{field_base}_en"

    if hasattr(obj, localized_field):
        val = getattr(obj, localized_field)
        if val:
            return val

    if hasattr(obj, fallback_field):
        return getattr(obj, fallback_field, [])

    return []
