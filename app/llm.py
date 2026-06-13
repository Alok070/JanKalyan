"""
Sarvam AI integration — LLM chat + Translate + template fallback.

Uses:
- Sarvam chat completions API for natural language understanding and grounded answers
- Sarvam Translate API for translating LLM outputs to user's language
- Template-based formatting as fast deterministic fallback
"""

import logging
from typing import Optional
import httpx
from app.config import settings
from app.prompts import SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE, EXTRACT_PROMPT
from app.models import SchemeRecord
from app.language import get_localized, get_localized_list

logger = logging.getLogger(__name__)

# Reusable async client — avoids creating a new connection per call
_http_client: Optional[httpx.AsyncClient] = None


async def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=25.0)
    return _http_client


# ═══════════════════════════════════════════════════════════════════════════
#  Sarvam Chat Completions
# ═══════════════════════════════════════════════════════════════════════════

async def chat_with_llm(
    user_message: str,
    scheme_context: str,
    language: str,
    system_prompt: str | None = None,
    max_tokens: int = 500,
    temperature: float = 0.3,
) -> Optional[str]:
    """
    Send a grounded query to Sarvam LLM.
    Returns None if the API is unavailable (triggers template fallback).
    """
    if not settings.sarvam_api_key:
        return None

    lang_name = {"en": "English", "hi": "Hindi", "ta": "Tamil"}.get(language, "English")

    prompt = RAG_PROMPT_TEMPLATE.format(
        scheme_data=scheme_context,
        question=user_message,
        language=lang_name,
    )

    sys_prompt = system_prompt or SYSTEM_PROMPT

    try:
        client = await _get_client()
        resp = await client.post(
            f"{settings.sarvam_base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.sarvam_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sarvam-m",
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        else:
            logger.warning(f"Sarvam LLM {resp.status_code}: {resp.text[:300]}")
            return None
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None


async def extract_with_llm(user_message: str, field: str) -> Optional[str]:
    """
    Use LLM to extract structured data from natural language input.
    e.g. "main UP se hoon" → extracts state="Uttar Pradesh"
    e.g. "main kisan hoon" → extracts occupation="farmer"
    """
    if not settings.sarvam_api_key:
        return None

    prompt = EXTRACT_PROMPT.format(field=field, user_input=user_message)

    try:
        client = await _get_client()
        resp = await client.post(
            f"{settings.sarvam_base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.sarvam_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sarvam-m",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.1,
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        logger.error(f"Extract LLM failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  Sarvam Translate
# ═══════════════════════════════════════════════════════════════════════════

SARVAM_LANG_CODES = {"en": "en-IN", "hi": "hi-IN", "ta": "ta-IN"}


async def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate using Sarvam Translate API. Falls back to original text."""
    if source_lang == target_lang or not text.strip():
        return text
    if not settings.sarvam_api_key:
        return text

    src = SARVAM_LANG_CODES.get(source_lang, "en-IN")
    tgt = SARVAM_LANG_CODES.get(target_lang, "en-IN")

    try:
        client = await _get_client()
        resp = await client.post(
            f"{settings.sarvam_base_url}/translate",
            headers={
                "api-subscription-key": settings.sarvam_api_key,
                "Content-Type": "application/json",
            },
            json={
                "input": text,
                "source_language_code": src,
                "target_language_code": tgt,
                "mode": "formal",
                "enable_preprocessing": True,
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("translated_text", text)
        else:
            logger.warning(f"Translate {resp.status_code}: {resp.text[:200]}")
            return text
    except Exception as e:
        logger.error(f"Translate failed: {e}")
        return text


# ═══════════════════════════════════════════════════════════════════════════
#  Localized labels & template formatters
# ═══════════════════════════════════════════════════════════════════════════

_LABELS = {
    "en": {"docs": "Documents needed", "benefit": "Benefits", "about": "About",
           "who": "Who can apply", "source": "Source", "apply_tip": "How to apply"},
    "hi": {"docs": "ज़रूरी दस्तावेज़", "benefit": "लाभ", "about": "जानकारी",
           "who": "कौन आवेदन कर सकता है", "source": "स्रोत", "apply_tip": "आवेदन कैसे करें"},
    "ta": {"docs": "தேவையான ஆவணங்கள்", "benefit": "பயன்கள்", "about": "பற்றி",
           "who": "யார் விண்ணப்பிக்கலாம்", "source": "ஆதாரம்", "apply_tip": "விண்ணப்பிப்பது எப்படி"},
}


def _get_labels(lang: str) -> dict:
    return _LABELS.get(lang, _LABELS["en"])


def format_scheme_result(scheme: SchemeRecord, reasons: list[str], lang: str) -> str:
    """Short scheme card for results list."""
    labels = _get_labels(lang)
    name = get_localized(scheme, "name", lang)
    eligibility = get_localized(scheme, "eligibility_summary", lang)
    benefits = get_localized(scheme, "benefits", lang)
    documents = get_localized_list(scheme, "documents", lang)

    doc_list = "\n".join(f"  {i+1}. {doc}" for i, doc in enumerate(documents))

    result = f"📋 *{name}*\n"
    result += f"✅ {eligibility}\n"
    result += f"💰 {benefits}\n"
    result += f"📄 *{labels['docs']}:*\n{doc_list}\n"
    result += f"🔗 {scheme.official_url}\n"

    return result


def format_scheme_checklist(scheme: SchemeRecord, lang: str) -> str:
    """Copy-paste friendly document checklist for SMS/WhatsApp."""
    name = get_localized(scheme, "name", lang)
    documents = get_localized_list(scheme, "documents", lang)

    header = {
        "en": f"📋 DOCUMENT CHECKLIST\nScheme: {name}\n{'─' * 25}",
        "hi": f"📋 दस्तावेज़ चेकलिस्ट\nयोजना: {name}\n{'─' * 25}",
        "ta": f"📋 ஆவண பட்டியல்\nதிட்டம்: {name}\n{'─' * 25}",
    }.get(lang, f"📋 DOCUMENT CHECKLIST\nScheme: {name}\n{'─' * 25}")

    items = "\n".join(f"☐ {i+1}. {doc}" for i, doc in enumerate(documents))

    footer = {
        "en": f"\n{'─' * 25}\n🔗 Apply: {scheme.official_url}\n✅ Collect all documents before visiting the office.",
        "hi": f"\n{'─' * 25}\n🔗 आवेदन: {scheme.official_url}\n✅ कार्यालय जाने से पहले सभी दस्तावेज़ इकट्ठा करें।",
        "ta": f"\n{'─' * 25}\n🔗 விண்ணப்பம்: {scheme.official_url}\n✅ அலுவலகம் செல்வதற்கு முன் அனைத்து ஆவணங்களையும் சேகரிக்கவும்.",
    }.get(lang, f"\n{'─' * 25}\n🔗 Apply: {scheme.official_url}")

    return f"{header}\n{items}{footer}"


def format_scheme_detail(scheme: SchemeRecord, lang: str) -> str:
    """Detailed view of a single scheme."""
    labels = _get_labels(lang)
    name = get_localized(scheme, "name", lang)
    description = get_localized(scheme, "description", lang)
    eligibility = get_localized(scheme, "eligibility_summary", lang)
    benefits = get_localized(scheme, "benefits", lang)
    documents = get_localized_list(scheme, "documents", lang)

    doc_list = "\n".join(f"  {i+1}. {doc}" for i, doc in enumerate(documents))

    result = f"📋 *{name}*\n\n"
    result += f"ℹ️ *{labels['about']}:* {description}\n\n"
    result += f"👤 *{labels['who']}:* {eligibility}\n\n"
    result += f"💰 *{labels['benefit']}:* {benefits}\n\n"
    result += f"📄 *{labels['docs']}:*\n{doc_list}\n\n"
    result += f"🔗 *{labels['source']}:* {scheme.official_url}\n"
    result += f"    ({scheme.source})"

    return result


def build_scheme_context(schemes: list) -> str:
    """Build rich context string for LLM grounding from scheme list."""
    parts = []
    for m in schemes:
        s = m.scheme if hasattr(m, "scheme") else m
        parts.append(
            f"Scheme: {s.name_en} / {s.name_hi}\n"
            f"Category: {s.category}\n"
            f"Description: {s.description_en}\n"
            f"Eligibility: {s.eligibility_summary_en}\n"
            f"Benefits: {s.benefits_en}\n"
            f"Documents: {', '.join(s.documents_en)}\n"
            f"Official URL: {s.official_url}\n"
            f"Source: {s.source}"
        )
    return "\n\n---\n\n".join(parts)
