"""Pydantic models for schemes, user profiles, and chat messages."""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Scheme record — stored in SQLite, returned by retrieval
# ---------------------------------------------------------------------------

class SchemeEligibility(BaseModel):
    """Structured eligibility criteria for rule-based matching."""
    min_age: int = 0
    max_age: int = 120
    gender: list[str] = ["male", "female", "other"]          # who can apply
    occupations: list[str] = []                               # [] means any
    max_monthly_income: int = 0                               # 0 = no limit
    states: list[str] = []                                    # [] = all-India
    categories: list[str] = []                                # BPL, APL, SC, ST, etc.
    extra_conditions: list[str] = []                          # free-text rules


class SchemeRecord(BaseModel):
    """One welfare scheme — the single source of truth."""
    id: str
    name_en: str
    name_hi: str
    name_ta: str
    category: str                             # pension, housing, agriculture…
    description_en: str
    description_hi: str
    description_ta: str
    eligibility: SchemeEligibility
    eligibility_summary_en: str
    eligibility_summary_hi: str
    eligibility_summary_ta: str
    documents_en: list[str]
    documents_hi: list[str]
    documents_ta: list[str]
    benefits_en: str
    benefits_hi: str
    benefits_ta: str
    official_url: str
    source: str = "myScheme.gov.in"


# ---------------------------------------------------------------------------
# User profile — built turn-by-turn during conversation
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    state: str = ""
    age: int = 0
    gender: str = ""
    occupation: str = ""
    monthly_income: int = 0
    existing_benefits: str = "none"  # none, ration_bpl, pension, other_scheme, unsure


# ---------------------------------------------------------------------------
# Chat message
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str          # "user" or "assistant"
    content: str
    language: str = "en"


# ---------------------------------------------------------------------------
# Matched scheme result
# ---------------------------------------------------------------------------

class SchemeMatch(BaseModel):
    scheme: SchemeRecord
    match_score: float = 0.0
    match_reasons: list[str] = []
