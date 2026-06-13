"""
Conversation state machine for the eligibility flow.

States: GREETING → STATE → AGE → GENDER → OCCUPATION → INCOME → EXISTING_BENEFITS → RESULTS → FREE_CHAT

Features:
- 6-turn eligibility intake with validation
- LLM-assisted parsing for natural language inputs (via Sarvam)
- Language re-detection per turn (supports mid-conversation switching)
- Code-mixed input handling
- Smart free-chat with RAG-grounded LLM answers
- Aadhaar/document query routing
"""

import logging
import re
from enum import Enum
from typing import Optional

from app.models import UserProfile, SchemeMatch
from app.language import detect_language, is_code_mixed, get_localized, get_localized_list
from app.prompts import QUESTIONS
from app.retrieval import match_schemes, normalize_state, normalize_occupation, search_by_query
from app.llm import (
    format_scheme_result, format_scheme_checklist, format_scheme_detail,
    chat_with_llm, extract_with_llm, translate_text, build_scheme_context,
)
from app.db import get_all_schemes, row_to_scheme

logger = logging.getLogger(__name__)


class ConvState(str, Enum):
    GREETING = "greeting"
    STATE = "state"
    AGE = "age"
    GENDER = "gender"
    OCCUPATION = "occupation"
    INCOME = "income"
    EXISTING_BENEFITS = "existing_benefits"
    RESULTS = "results"
    FREE_CHAT = "free_chat"


class UserSession:
    """Per-user session holding conversation state and profile."""

    def __init__(self):
        self.state: ConvState = ConvState.GREETING
        self.profile: UserProfile = UserProfile()
        self.language: str = "en"
        self.matched_schemes: list[SchemeMatch] = []
        self.turn_count: int = 0
        self.existing_benefits: str = "none"


# In-memory session store (phone_number → session)
_sessions: dict[str, UserSession] = {}


def get_session(user_id: str) -> UserSession:
    if user_id not in _sessions:
        _sessions[user_id] = UserSession()
    return _sessions[user_id]


def reset_session(user_id: str):
    _sessions[user_id] = UserSession()


def _get_question(key: str, lang: str) -> str:
    """Get a localized question template."""
    q = QUESTIONS.get(key, {})
    return q.get(lang, q.get("en", ""))


# ═══════════════════════════════════════════════════════════════════════════
#  Input parsers — rule-based first, LLM fallback
# ═══════════════════════════════════════════════════════════════════════════

def _parse_age(text: str) -> Optional[int]:
    """Extract age from text."""
    nums = re.findall(r"\d+", text)
    if nums:
        age = int(nums[0])
        if 0 < age < 130:
            return age
    return None


def _parse_gender(text: str) -> Optional[str]:
    """Parse gender from text or number selection."""
    text_lower = text.strip().lower()

    # Number selection
    if text_lower in ("1", "1️⃣"):
        return "male"
    if text_lower in ("2", "2️⃣"):
        return "female"
    if text_lower in ("3", "3️⃣"):
        return "other"

    # Text matching (multilingual)
    male_words = ["male", "man", "boy", "पुरुष", "आदमी", "लड़का", "mard", "ஆண்", "m"]
    female_words = ["female", "woman", "girl", "महिला", "औरत", "लड़की", "स्त्री", "aurat", "பெண்", "f"]
    other_words = ["other", "अन्य", "பிற", "trans"]

    for w in male_words:
        if w in text_lower:
            return "male"
    for w in female_words:
        if w in text_lower:
            return "female"
    for w in other_words:
        if w in text_lower:
            return "other"

    return None


def _parse_occupation(text: str) -> Optional[str]:
    """Parse occupation from text or number selection."""
    text_lower = text.strip().lower()

    # Number selection
    occ_map = {
        "1": "farmer", "1️⃣": "farmer",
        "2": "laborer", "2️⃣": "laborer",
        "3": "student", "3️⃣": "student",
        "4": "homemaker", "4️⃣": "homemaker",
        "5": "artisan", "5️⃣": "artisan",
        "6": "other", "6️⃣": "other",
    }
    if text_lower in occ_map:
        return occ_map[text_lower]

    # Use the normalization function
    normalized = normalize_occupation(text)
    return normalized


def _parse_income(text: str) -> Optional[int]:
    """Parse income band from text or number selection."""
    text_lower = text.strip().lower()

    # Number selection
    if text_lower in ("1", "1️⃣"):
        return 8000  # midpoint of < ₹10,000
    if text_lower in ("2", "2️⃣"):
        return 17000  # midpoint of ₹10,000–₹25,000
    if text_lower in ("3", "3️⃣"):
        return 35000  # representative of > ₹25,000

    # Hindi/Tamil text patterns for income bands
    low_words = ["kam", "कम", "गरीब", "poor", "குறைவு", "low"]
    high_words = ["zyada", "ज़्यादा", "अधिक", "high", "rich", "அதிகம்"]
    if any(w in text_lower for w in low_words):
        return 8000
    if any(w in text_lower for w in high_words):
        return 35000

    # Try to extract a number
    nums = re.findall(r"\d+", text.replace(",", ""))
    if nums:
        val = int(nums[0])
        if val > 1000:  # Assume it's monthly income
            return val
        elif val <= 100:  # Might be in thousands
            return val * 1000

    return None


def _parse_existing_benefits(text: str) -> str:
    """Parse existing benefits selection."""
    text_lower = text.strip().lower()
    benefit_map = {
        "1": "none", "1️⃣": "none",
        "2": "ration_bpl", "2️⃣": "ration_bpl",
        "3": "pension", "3️⃣": "pension",
        "4": "other_scheme", "4️⃣": "other_scheme",
        "5": "unsure", "5️⃣": "unsure",
    }
    if text_lower in benefit_map:
        return benefit_map[text_lower]

    # Text matching
    if any(w in text_lower for w in ["no", "nahi", "नहीं", "कोई नहीं", "இல்லை"]):
        return "none"
    if any(w in text_lower for w in ["ration", "राशन", "bpl", "ரேஷன்"]):
        return "ration_bpl"
    if any(w in text_lower for w in ["pension", "पेंशन", "ஓய்வூதியம்"]):
        return "pension"

    return "unsure"


# ═══════════════════════════════════════════════════════════════════════════
#  Intent detection — identifies what the user is trying to do
# ═══════════════════════════════════════════════════════════════════════════

def _detect_intent(text: str) -> str:
    """Detect user intent from free-text input."""
    text_lower = text.lower().strip()

    # Aadhaar-related queries
    aadhaar_words = ["aadhaar", "aadhar", "आधार", "uidai", "aadhaar card", "आதார்"]
    if any(w in text_lower for w in aadhaar_words):
        return "aadhaar_help"

    # Document / checklist request
    doc_words = ["checklist", "document", "दस्तावेज़", "कागज", "kagaz", "ஆவணம்", "பட்டியல்", "list", "papers"]
    if any(w in text_lower for w in doc_words):
        return "checklist"

    # Application process
    apply_words = ["apply", "kaise", "कैसे", "आवेदन", "registration", "register", "எப்படி", "விண்ணப்பம்", "how to"]
    if any(w in text_lower for w in apply_words):
        return "how_to_apply"

    # Eligibility questions
    eligible_words = ["eligible", "qualify", "योग्य", "पात्र", "milega", "मिलेगा", "தகுதி", "கிடைக்கும்"]
    if any(w in text_lower for w in eligible_words):
        return "eligibility_check"

    # Scheme query — check if user mentions a scheme name
    return "general"


# ═══════════════════════════════════════════════════════════════════════════
#  Main handler
# ═══════════════════════════════════════════════════════════════════════════

async def handle_message(user_id: str, text: str) -> str:
    """
    Process user message and return bot response.
    This is the core function called by both WhatsApp webhook and web simulator.
    """
    session = get_session(user_id)
    text = text.strip()

    # Re-detect language every turn (supports mid-conversation switching)
    detected_lang = detect_language(text)
    if session.turn_count == 0:
        session.language = detected_lang
    elif detected_lang != "en":
        # Only switch if user clearly types in a non-English script
        session.language = detected_lang

    lang = session.language

    # --- Global commands ---
    text_lower = text.lower()
    if text_lower in ("reset", "start", "restart", "शुरू", "रीसेट", "மீட்டமை", "hi", "hello", "नमस्ते"):
        # If in FREE_CHAT and text is a greeting, redirect to start over
        if session.state == ConvState.FREE_CHAT or session.state == ConvState.GREETING:
            session_lang = detect_language(text)
            reset_session(user_id)
            session = get_session(user_id)
            session.language = session_lang
            session.state = ConvState.STATE
            session.turn_count = 1
            return _get_question("greeting", session.language)
        # If mid-flow, only reset on explicit reset commands
        if text_lower in ("reset", "restart", "रीसेट", "மீட்டமை"):
            session_lang = detect_language(text)
            reset_session(user_id)
            session = get_session(user_id)
            session.language = session_lang
            session.state = ConvState.STATE
            session.turn_count = 1
            return _get_question("greeting", session.language)

    # --- Greeting / first message ---
    if session.state == ConvState.GREETING:
        session.language = detect_language(text)
        lang = session.language
        session.state = ConvState.STATE
        session.turn_count += 1
        return _get_question("greeting", lang)

    # --- State ---
    if session.state == ConvState.STATE:
        # Try rule-based normalization first
        state_val = normalize_state(text.strip())
        if state_val == text.strip().lower():
            # Normalization didn't change anything — try LLM extraction for complex inputs
            llm_state = await extract_with_llm(text, "state")
            if llm_state and llm_state.lower() != "unknown":
                state_val = llm_state
            else:
                state_val = text.strip()

        session.profile.state = state_val
        session.state = ConvState.AGE
        session.turn_count += 1
        return _get_question("age", lang)

    # --- Age ---
    if session.state == ConvState.AGE:
        age = _parse_age(text)
        if age is None:
            # Try LLM for natural language age inputs like "pacchis saal"
            llm_age = await extract_with_llm(text, "age")
            if llm_age:
                age = _parse_age(llm_age)
        if age is None:
            retry = {
                "en": "Please enter a valid age (number only), e.g., 35",
                "hi": "कृपया सही उम्र डालें (सिर्फ नंबर), जैसे 35",
                "ta": "சரியான வயதை உள்ளிடவும் (எண் மட்டும்), எ.கா., 35",
            }
            return retry.get(lang, retry["en"])
        session.profile.age = age
        session.state = ConvState.GENDER
        session.turn_count += 1
        return _get_question("gender", lang)

    # --- Gender ---
    if session.state == ConvState.GENDER:
        gender = _parse_gender(text)
        if gender is None:
            # Try LLM for ambiguous gender inputs
            llm_gender = await extract_with_llm(text, "gender")
            if llm_gender and llm_gender.lower() in ("male", "female", "other"):
                gender = llm_gender.lower()
        if gender is None:
            retry = {
                "en": "Please select 1, 2, or 3:\n1️⃣ Male\n2️⃣ Female\n3️⃣ Other",
                "hi": "कृपया 1, 2, या 3 चुनें:\n1️⃣ पुरुष\n2️⃣ महिला\n3️⃣ अन्य",
                "ta": "1, 2, அல்லது 3 தேர்வு செய்யவும்:\n1️⃣ ஆண்\n2️⃣ பெண்\n3️⃣ பிற",
            }
            return retry.get(lang, retry["en"])
        session.profile.gender = gender
        session.state = ConvState.OCCUPATION
        session.turn_count += 1
        return _get_question("occupation", lang)

    # --- Occupation ---
    if session.state == ConvState.OCCUPATION:
        occupation = _parse_occupation(text)
        if occupation == "other":
            # Try LLM for natural language occupation like "main khet mein kaam karta hoon"
            llm_occ = await extract_with_llm(text, "occupation")
            if llm_occ and llm_occ.lower() in ("farmer", "laborer", "student", "homemaker", "artisan"):
                occupation = llm_occ.lower()
        session.profile.occupation = occupation or "other"
        session.state = ConvState.INCOME
        session.turn_count += 1
        return _get_question("income", lang)

    # --- Income ---
    if session.state == ConvState.INCOME:
        income = _parse_income(text)
        if income is None:
            # Try LLM for natural language income
            llm_income = await extract_with_llm(text, "income_band")
            if llm_income:
                band = llm_income.lower().strip()
                income = {"low": 8000, "medium": 17000, "high": 35000}.get(band)
        if income is None:
            retry = {
                "en": "Please select 1, 2, or 3:\n1️⃣ Less than ₹10,000\n2️⃣ ₹10,000 – ₹25,000\n3️⃣ More than ₹25,000",
                "hi": "कृपया 1, 2, या 3 चुनें:\n1️⃣ ₹10,000 से कम\n2️⃣ ₹10,000 – ₹25,000\n3️⃣ ₹25,000 से अधिक",
                "ta": "1, 2, அல்லது 3 தேர்வு செய்யவும்:\n1️⃣ ₹10,000 க்கும் குறைவு\n2️⃣ ₹10,000 – ₹25,000\n3️⃣ ₹25,000 க்கும் அதிகம்",
            }
            return retry.get(lang, retry["en"])
        session.profile.monthly_income = income
        session.state = ConvState.EXISTING_BENEFITS
        session.turn_count += 1
        return _get_question("existing_benefits", lang)

    # --- Existing Benefits (6th question) ---
    if session.state == ConvState.EXISTING_BENEFITS:
        session.existing_benefits = _parse_existing_benefits(text)
        session.state = ConvState.RESULTS
        session.turn_count += 1

        # --- Generate results ---
        return await _generate_results(session, lang)

    # --- Free chat (after results) ---
    if session.state == ConvState.FREE_CHAT:
        return await _handle_free_chat(session, text, lang)

    # Fallback
    return _get_question("unknown", lang)


async def _generate_results(session: UserSession, lang: str) -> str:
    """Run eligibility matching and format results."""
    matches = match_schemes(session.profile)
    session.matched_schemes = matches

    if not matches:
        session.state = ConvState.FREE_CHAT
        return _get_question("no_results", lang)

    # Format results
    header = _get_question("results_header", lang)
    result_parts = []

    for i, match in enumerate(matches[:5]):  # Show max 5
        result_parts.append(format_scheme_result(match.scheme, match.match_reasons, lang))

    footer = _get_question("ask_more", lang)

    session.state = ConvState.FREE_CHAT
    return header + "\n".join(result_parts) + footer


async def _handle_free_chat(session: UserSession, text: str, lang: str) -> str:
    """
    Handle questions after results have been shown.
    Uses intent detection + scheme matching + LLM for smart responses.
    """
    text_lower = text.lower().strip()
    intent = _detect_intent(text)

    # ── Aadhaar help ──────────────────────────────────────────────────────
    if intent == "aadhaar_help":
        aadhaar_response = {
            "en": (
                "📌 *Aadhaar Help*\n\n"
                "For Aadhaar-related issues:\n"
                "1. *Lost Aadhaar*: Download e-Aadhaar at https://eaadhaar.uidai.gov.in\n"
                "2. *Update Aadhaar*: Visit https://ssup.uidai.gov.in\n"
                "3. *Helpline*: Call 1947 (toll-free)\n"
                "4. *Nearest center*: Visit https://appointments.uidai.gov.in\n\n"
                "⚠️ I can only help with welfare schemes. For Aadhaar issues, please use the links above."
            ),
            "hi": (
                "📌 *आधार मदद*\n\n"
                "आधार से जुड़ी समस्याओं के लिए:\n"
                "1. *आधार खो गया*: e-Aadhaar डाउनलोड करें — https://eaadhaar.uidai.gov.in\n"
                "2. *आधार अपडेट*: https://ssup.uidai.gov.in\n"
                "3. *हेल्पलाइन*: 1947 पर कॉल करें (मुफ्त)\n"
                "4. *नज़दीकी केंद्र*: https://appointments.uidai.gov.in\n\n"
                "⚠️ मैं सिर्फ सरकारी योजनाओं में मदद कर सकता हूँ। आधार की समस्या के लिए ऊपर दिए गए लिंक देखें।"
            ),
            "ta": (
                "📌 *ஆதார் உதவி*\n\n"
                "ஆதார் தொடர்பான பிரச்சனைகளுக்கு:\n"
                "1. *ஆதார் தொலைந்தது*: e-Aadhaar பதிவிறக்கம் — https://eaadhaar.uidai.gov.in\n"
                "2. *ஆதார் புதுப்பிப்பு*: https://ssup.uidai.gov.in\n"
                "3. *உதவி எண்*: 1947 (இலவசம்)\n"
                "4. *அருகிலுள்ள மையம்*: https://appointments.uidai.gov.in\n\n"
                "⚠️ நான் அரசு நலத்திட்டங்களில் மட்டுமே உதவ முடியும்."
            ),
        }
        return aadhaar_response.get(lang, aadhaar_response["en"])

    # ── Document checklist ────────────────────────────────────────────────
    if intent == "checklist":
        if session.matched_schemes:
            checklists = []
            for match in session.matched_schemes[:3]:
                checklists.append(format_scheme_checklist(match.scheme, lang))
            return "\n\n".join(checklists)
        return _get_question("unknown", lang)

    # ── Scheme name matching (robust: Hindi, Tamil, romanized, keywords) ──
    # Common romanized keywords for each scheme
    SCHEME_KEYWORDS = {
        "pm_kisan": ["kisan", "pm-kisan", "pm kisan", "किसान सम्मान", "kisan samman"],
        "ayushman_bharat": ["ayushman", "pmjay", "pm-jay", "आयुष्मान", "health card", "ஆயுஷ்மான்"],
        "pmay": ["pmay", "awas", "housing", "आवास", "ghar", "makan", "வீடு"],
        "ujjwala": ["ujjwala", "gas", "cylinder", "lpg", "उज्ज्वला", "गैस", "சிலிண்டர்"],
        "mgnrega": ["mgnrega", "nrega", "manrega", "mnrega", "मनरेगा", "rozgar", "mazdoor"],
        "sukanya_samriddhi": ["sukanya", "samriddhi", "ssy", "सुकन्या", "beti", "daughter"],
        "atal_pension": ["atal pension", "apy", "pension", "अटल", "पेंशन", "ஓய்வூதியம்"],
        "pm_vishwakarma": ["vishwakarma", "karigar", "artisan", "craft", "विश्वकर्मा", "शिल्पकार"],
        "kisan_credit_card": ["kcc", "kisan credit", "credit card", "क्रेडिट", "किसान कार्ड", "loan"],
        "ladli_behna_mp": ["ladli", "behna", "bahna", "लाड़ली", "बहना", "ladli behna"],
    }

    def _find_scheme_by_keywords(query: str):
        """Try to match a scheme by keywords in user query."""
        query_lower = query.lower()
        for scheme_id, keywords in SCHEME_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    return scheme_id
        return None

    # Try keyword matching first
    matched_scheme_id = _find_scheme_by_keywords(text)
    if matched_scheme_id:
        # Find in matched schemes first
        for match in session.matched_schemes:
            if match.scheme.id == matched_scheme_id:
                if intent == "how_to_apply":
                    detail = format_scheme_detail(match.scheme, lang)
                    apply_tip = {
                        "en": f"\n\n📝 *How to apply:*\nVisit {match.scheme.official_url} or your nearest CSC (Common Service Centre).",
                        "hi": f"\n\n📝 *आवेदन कैसे करें:*\n{match.scheme.official_url} पर जाएं या अपने नज़दीकी CSC (जन सेवा केंद्र) पर जाएं।",
                        "ta": f"\n\n📝 *விண்ணப்பிப்பது எப்படி:*\n{match.scheme.official_url} அல்லது அருகிலுள்ள CSC (பொது சேவை மையம்) செல்லவும்.",
                    }
                    return detail + apply_tip.get(lang, apply_tip["en"])
                return format_scheme_detail(match.scheme, lang)
        # Fallback: search all schemes
        all_rows = get_all_schemes()
        for row in all_rows:
            scheme = row_to_scheme(row)
            if scheme.id == matched_scheme_id:
                return format_scheme_detail(scheme, lang)

    # Exact name match (Devanagari/Tamil/English)
    for match in session.matched_schemes:
        scheme = match.scheme
        name_check = [
            scheme.id.replace("_", " "),
            scheme.name_en.lower(),
            scheme.name_hi.lower() if scheme.name_hi else "",
            scheme.name_ta.lower() if scheme.name_ta else "",
            scheme.id.lower(),
            scheme.name_en.split("(")[0].strip().lower() if "(" in scheme.name_en else "",
        ]
        for name in name_check:
            if name and len(name) > 2 and (name in text_lower or text_lower in name):
                return format_scheme_detail(scheme, lang)

    # Search ALL schemes by exact name
    all_rows = get_all_schemes()
    for row in all_rows:
        scheme = row_to_scheme(row)
        name_check = [
            scheme.id.replace("_", " "), scheme.name_en.lower(), scheme.id.lower(),
        ]
        for name in name_check:
            if name and len(name) > 2 and (name in text_lower or text_lower in name):
                return format_scheme_detail(scheme, lang)

    # ── LLM-powered response (RAG grounded in ALL schemes) ────────────────
    all_rows = get_all_schemes()
    all_scheme_objects = [row_to_scheme(row) for row in all_rows]
    # Always use all schemes for context so LLM can answer about any scheme
    context = build_scheme_context(
        [type('M', (), {'scheme': s})() for s in all_scheme_objects]
    )

    llm_response = await chat_with_llm(text, context, lang)
    if llm_response:
        return llm_response

    # ── Template fallback ─────────────────────────────────────────────────
    return _get_question("unknown", lang)
