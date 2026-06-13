"""
Test the retrieval engine — eligibility matching and FTS search.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import UserProfile
from app.db import init_db, insert_scheme, get_all_schemes
from app.schemes_data import SCHEMES
from app.retrieval import match_schemes, normalize_occupation, normalize_state
from app.config import settings


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    """Use a temp database for tests."""
    settings.database_path = str(tmp_path / "test_schemes.db")
    init_db()
    for scheme in SCHEMES:
        insert_scheme(scheme)


class TestNormalization:
    def test_normalize_occupation_english(self):
        assert normalize_occupation("farmer") == "farmer"
        assert normalize_occupation("Farmer") == "farmer"

    def test_normalize_occupation_hindi(self):
        assert normalize_occupation("किसान") == "farmer"
        assert normalize_occupation("मजदूर") == "laborer"

    def test_normalize_occupation_unknown(self):
        assert normalize_occupation("xyz") == "other"

    def test_normalize_state(self):
        assert normalize_state("MP") == "madhya pradesh"
        assert normalize_state("मध्य प्रदेश") == "madhya pradesh"
        assert normalize_state("tamil nadu") == "tamil nadu"


class TestEligibilityMatching:
    def test_farmer_gets_pm_kisan(self):
        profile = UserProfile(state="UP", age=35, gender="male", occupation="farmer", monthly_income=8000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "pm_kisan" in scheme_ids

    def test_farmer_gets_kcc(self):
        profile = UserProfile(state="UP", age=35, gender="male", occupation="farmer", monthly_income=8000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "kisan_credit_card" in scheme_ids

    def test_woman_bpl_gets_ujjwala(self):
        profile = UserProfile(state="Bihar", age=30, gender="female", occupation="homemaker", monthly_income=8000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "ujjwala" in scheme_ids

    def test_mp_woman_gets_ladli_behna(self):
        profile = UserProfile(state="MP", age=30, gender="female", occupation="homemaker", monthly_income=15000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "ladli_behna_mp" in scheme_ids

    def test_non_mp_woman_no_ladli_behna(self):
        profile = UserProfile(state="UP", age=30, gender="female", occupation="homemaker", monthly_income=15000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "ladli_behna_mp" not in scheme_ids

    def test_young_person_gets_atal_pension(self):
        profile = UserProfile(state="TN", age=25, gender="male", occupation="laborer", monthly_income=8000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "atal_pension" in scheme_ids

    def test_old_person_no_atal_pension(self):
        profile = UserProfile(state="TN", age=50, gender="male", occupation="laborer", monthly_income=8000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "atal_pension" not in scheme_ids

    def test_laborer_gets_mgnrega(self):
        profile = UserProfile(state="Bihar", age=40, gender="male", occupation="laborer", monthly_income=8000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "mgnrega" in scheme_ids

    def test_artisan_gets_vishwakarma(self):
        profile = UserProfile(state="UP", age=35, gender="male", occupation="artisan", monthly_income=8000)
        matches = match_schemes(profile)
        scheme_ids = [m.scheme.id for m in matches]
        assert "pm_vishwakarma" in scheme_ids

    def test_all_schemes_loaded(self):
        schemes = get_all_schemes()
        assert len(schemes) == 10


class TestDatabaseIntegrity:
    def test_scheme_has_trilingual_names(self):
        schemes = get_all_schemes()
        for s in schemes:
            assert s["name_en"], f"Scheme {s['id']} missing name_en"
            assert s["name_hi"], f"Scheme {s['id']} missing name_hi"
            assert s["name_ta"], f"Scheme {s['id']} missing name_ta"

    def test_scheme_has_official_url(self):
        schemes = get_all_schemes()
        for s in schemes:
            assert s["official_url"].startswith("http"), f"Scheme {s['id']} missing URL"
