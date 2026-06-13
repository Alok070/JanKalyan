"""
End-to-end conversation tests — Hindi, Tamil, code-mixed, reset, Aadhaar queries.
Tests the full conversation state machine including the 6th question (existing benefits).
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.conversation import handle_message, reset_session, get_session
from app.db import init_db, insert_scheme
from app.schemes_data import SCHEMES
from app.language import detect_language, is_code_mixed
from app.config import settings


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    """Use a temp database for tests."""
    settings.database_path = str(tmp_path / "test_conv.db")
    init_db()
    for scheme in SCHEMES:
        insert_scheme(scheme)


class TestLanguageDetection:
    def test_detect_hindi(self):
        assert detect_language("नमस्ते") == "hi"
        assert detect_language("मेरा नाम राम है") == "hi"

    def test_detect_tamil(self):
        assert detect_language("வணக்கம்") == "ta"
        assert detect_language("என் பெயர் ராம்") == "ta"

    def test_detect_english(self):
        assert detect_language("Hello") == "en"
        assert detect_language("My name is Ram") == "en"

    def test_code_mixed(self):
        assert is_code_mixed("मेरा aadhaar खो गया") is True
        assert is_code_mixed("Hello world") is False


class TestHindiConversation:
    """
    Full 6-turn Hindi conversation flow:
    User: नमस्ते → state → age → gender → occupation → income → existing_benefits → results
    """

    @pytest.mark.asyncio
    async def test_hindi_full_flow(self):
        user_id = "hindi_test_user"
        reset_session(user_id)

        # Turn 0: Greeting
        reply = await handle_message(user_id, "नमस्ते")
        assert "राज्य" in reply or "state" in reply.lower()

        # Turn 1: State
        reply = await handle_message(user_id, "उत्तर प्रदेश")
        assert "उम्र" in reply or "age" in reply.lower()

        # Turn 2: Age
        reply = await handle_message(user_id, "35")
        assert "लिंग" in reply or "gender" in reply.lower() or "पुरुष" in reply

        # Turn 3: Gender
        reply = await handle_message(user_id, "1")
        assert "पेशा" in reply or "occupation" in reply.lower() or "किसान" in reply

        # Turn 4: Occupation
        reply = await handle_message(user_id, "1")  # Farmer
        assert "आय" in reply or "income" in reply.lower()

        # Turn 5: Income
        reply = await handle_message(user_id, "1")  # Less than ₹10,000
        # Should ask about existing benefits (6th question)
        assert "लाभ" in reply or "benefit" in reply.lower() or "राशन" in reply

        # Turn 6: Existing benefits
        reply = await handle_message(user_id, "1")  # None
        # Should show scheme results
        assert "PM-KISAN" in reply or "पीएम-किसान" in reply or "किसान" in reply


class TestTamilConversation:
    """
    Full Tamil conversation flow with 6 turns.
    """

    @pytest.mark.asyncio
    async def test_tamil_full_flow(self):
        user_id = "tamil_test_user"
        reset_session(user_id)

        # Turn 0: Greeting
        reply = await handle_message(user_id, "வணக்கம்")
        assert "மாநிலத்தில்" in reply or "state" in reply.lower()

        # Turn 1: State
        reply = await handle_message(user_id, "Tamil Nadu")
        assert "வயது" in reply or "age" in reply.lower()

        # Turn 2: Age
        reply = await handle_message(user_id, "28")
        assert "பாலினம்" in reply or "gender" in reply.lower() or "ஆண்" in reply

        # Turn 3: Gender — Female
        reply = await handle_message(user_id, "2")
        assert "தொழில்" in reply or "occupation" in reply.lower() or "விவசாயி" in reply

        # Turn 4: Occupation — Homemaker
        reply = await handle_message(user_id, "4")
        assert "வருமானம்" in reply or "income" in reply.lower()

        # Turn 5: Income — Less than ₹10,000
        reply = await handle_message(user_id, "1")
        # Should ask about existing benefits
        assert "உதவி" in reply or "benefit" in reply.lower() or "ரேஷன்" in reply or "இல்லை" in reply

        # Turn 6: Existing benefits — None
        reply = await handle_message(user_id, "1")
        # Should show scheme results
        assert "உஜ்வலா" in reply or "Ujjwala" in reply or "திட்ட" in reply


class TestCodeMixedInput:
    @pytest.mark.asyncio
    async def test_code_mixed_greeting(self):
        """Test that code-mixed input doesn't crash the bot."""
        user_id = "codemix_test"
        reset_session(user_id)

        reply = await handle_message(user_id, "मेरा aadhaar खो गया")
        # Bot should respond (in Hindi, since dominant script is Devanagari)
        assert reply is not None
        assert len(reply) > 0

    @pytest.mark.asyncio
    async def test_aadhaar_query_in_free_chat(self):
        """Test Aadhaar help response after results."""
        user_id = "aadhaar_test"
        reset_session(user_id)

        # Go through full flow quickly
        await handle_message(user_id, "Hi")
        await handle_message(user_id, "UP")
        await handle_message(user_id, "30")
        await handle_message(user_id, "1")  # male
        await handle_message(user_id, "1")  # farmer
        await handle_message(user_id, "1")  # low income
        await handle_message(user_id, "1")  # no existing benefits

        # Now ask about Aadhaar
        reply = await handle_message(user_id, "मेरा aadhaar खो गया")
        assert "aadhaar" in reply.lower() or "आधार" in reply or "uidai" in reply.lower()


class TestResetFlow:
    @pytest.mark.asyncio
    async def test_reset_mid_flow(self):
        user_id = "reset_test"
        reset_session(user_id)

        await handle_message(user_id, "Hi")
        await handle_message(user_id, "UP")

        # Reset mid-flow
        reply = await handle_message(user_id, "reset")
        assert "state" in reply.lower() or "राज्य" in reply or "மாநிலம்" in reply


class TestExistingBenefitsQuestion:
    @pytest.mark.asyncio
    async def test_existing_benefits_question_appears(self):
        """Verify the 6th question (existing benefits) is asked."""
        user_id = "benefits_test"
        reset_session(user_id)

        await handle_message(user_id, "Hi")
        await handle_message(user_id, "Bihar")
        await handle_message(user_id, "40")
        await handle_message(user_id, "1")  # male
        await handle_message(user_id, "2")  # laborer
        reply = await handle_message(user_id, "1")  # low income

        # Should be the existing benefits question, not results yet
        session = get_session(user_id)
        assert session.state.value == "existing_benefits"
