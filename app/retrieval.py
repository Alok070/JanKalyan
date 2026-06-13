"""
Retrieval engine — rule-based eligibility matching.

For 10 schemes, we don't need a vector DB. We use:
1. Structured rule matching (age, gender, income, occupation, state)
2. FTS5 keyword search as a secondary signal
3. Score-based ranking
"""

import json
import logging
from app.db import get_all_schemes, row_to_scheme, search_schemes_fts
from app.models import SchemeRecord, SchemeMatch, UserProfile

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Occupation normalization
# ---------------------------------------------------------------------------
OCCUPATION_MAP = {
    # English
    "farmer": "farmer",
    "kisan": "farmer",
    "laborer": "laborer",
    "labourer": "laborer",
    "mazdoor": "laborer",
    "worker": "laborer",
    "student": "student",
    "homemaker": "homemaker",
    "housewife": "homemaker",
    "artisan": "artisan",
    "craftsman": "artisan",
    "carpenter": "artisan",
    "blacksmith": "artisan",
    "potter": "artisan",
    "weaver": "artisan",
    "tailor": "artisan",
    "cobbler": "artisan",
    "goldsmith": "artisan",
    # Hindi
    "किसान": "farmer",
    "मजदूर": "laborer",
    "श्रमिक": "laborer",
    "छात्र": "student",
    "विद्यार्थी": "student",
    "गृहिणी": "homemaker",
    "कारीगर": "artisan",
    "बढ़ई": "artisan",
    "लोहार": "artisan",
    "कुम्हार": "artisan",
    "बुनकर": "artisan",
    "दर्जी": "artisan",
    # Tamil
    "விவசாயி": "farmer",
    "தொழிலாளி": "laborer",
    "மாணவர்": "student",
    "இல்லத்தரசி": "homemaker",
    "கைவினைஞர்": "artisan",
}

# State normalization
STATE_ALIASES = {
    "mp": "madhya pradesh",
    "म.प्र.": "madhya pradesh",
    "मध्य प्रदेश": "madhya pradesh",
    "மத்தியப் பிரதேசம்": "madhya pradesh",
    "up": "uttar pradesh",
    "उत्तर प्रदेश": "uttar pradesh",
    "bihar": "bihar",
    "बिहार": "bihar",
    "rajasthan": "rajasthan",
    "राजस्थान": "rajasthan",
    "tamil nadu": "tamil nadu",
    "tn": "tamil nadu",
    "தமிழ்நாடு": "tamil nadu",
    "maharashtra": "maharashtra",
    "महाराष्ट्र": "maharashtra",
    "karnataka": "karnataka",
    "कर्नाटक": "karnataka",
    "gujarat": "gujarat",
    "गुजरात": "gujarat",
    "west bengal": "west bengal",
    "पश्चिम बंगाल": "west bengal",
    "andhra pradesh": "andhra pradesh",
    "आंध्र प्रदेश": "andhra pradesh",
    "telangana": "telangana",
    "तेलंगाना": "telangana",
    "odisha": "odisha",
    "ओडिशा": "odisha",
    "punjab": "punjab",
    "पंजाब": "punjab",
    "haryana": "haryana",
    "हरियाणा": "haryana",
    "jharkhand": "jharkhand",
    "झारखंड": "jharkhand",
    "chhattisgarh": "chhattisgarh",
    "छत्तीसगढ़": "chhattisgarh",
    "kerala": "kerala",
    "केरल": "kerala",
}


def normalize_occupation(raw: str) -> str:
    """Normalize occupation input to a standard key."""
    raw_lower = raw.strip().lower()
    if raw_lower in OCCUPATION_MAP:
        return OCCUPATION_MAP[raw_lower]
    # Check if any key is a substring
    for key, val in OCCUPATION_MAP.items():
        if key in raw_lower or raw_lower in key:
            return val
    return "other"


def normalize_state(raw: str) -> str:
    """Normalize state input."""
    raw_lower = raw.strip().lower()
    if raw_lower in STATE_ALIASES:
        return STATE_ALIASES[raw_lower]
    # Direct match
    for alias, canonical in STATE_ALIASES.items():
        if alias in raw_lower or raw_lower in alias:
            return canonical
    # Check if any raw text matches
    for alias, canonical in STATE_ALIASES.items():
        if raw.strip() == alias:
            return canonical
    return raw_lower


def match_schemes(profile: UserProfile) -> list[SchemeMatch]:
    """
    Match user profile against all schemes using rule-based criteria.
    Returns a sorted list of SchemeMatch results.
    """
    all_rows = get_all_schemes()
    matches: list[SchemeMatch] = []

    normalized_state = normalize_state(profile.state) if profile.state else ""
    normalized_occupation = normalize_occupation(profile.occupation) if profile.occupation else "other"

    for row in all_rows:
        scheme = row_to_scheme(row)
        elig = scheme.eligibility
        score = 0.0
        reasons = []

        # --- Age check ---
        if profile.age > 0:
            if elig.min_age <= profile.age <= elig.max_age:
                score += 1.0
                reasons.append(f"Age {profile.age} is within {elig.min_age}–{elig.max_age}")
            else:
                continue  # Hard filter — skip if age doesn't match

        # --- Gender check ---
        if profile.gender:
            gender_lower = profile.gender.lower()
            if gender_lower in elig.gender:
                score += 1.0
                if "female" in elig.gender and len(elig.gender) == 1:
                    reasons.append("For women")
            else:
                continue  # Hard filter

        # --- Occupation check ---
        if elig.occupations:  # If scheme requires specific occupations
            if normalized_occupation in elig.occupations:
                score += 2.0  # Higher weight for occupation match
                reasons.append(f"Matches occupation: {normalized_occupation}")
            elif "other" in elig.occupations:
                score += 0.5
            else:
                continue  # Hard filter

        # --- Income check ---
        if elig.max_monthly_income > 0 and profile.monthly_income > 0:
            if profile.monthly_income <= elig.max_monthly_income:
                score += 1.0
                reasons.append(f"Income ₹{profile.monthly_income}/month is within limit")
            else:
                score -= 0.5  # Soft penalty, don't skip (user might qualify under other criteria)

        # --- State check ---
        if elig.states:  # State-specific scheme
            if normalized_state in elig.states:
                score += 2.0
                reasons.append(f"Available in {normalized_state}")
            else:
                continue  # Hard filter — state-specific scheme, wrong state

        # --- Base relevance ---
        if score > 0:
            score += 0.5  # Base score for passing all filters
            matches.append(SchemeMatch(scheme=scheme, match_score=score, match_reasons=reasons))

    # Sort by score descending
    matches.sort(key=lambda m: m.match_score, reverse=True)

    return matches[:5]  # Return top 5


def search_by_query(query: str) -> list[SchemeRecord]:
    """FTS5-based keyword search — used for free-form questions."""
    rows = search_schemes_fts(query)
    return [row_to_scheme(row) for row in rows]
