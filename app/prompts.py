"""
Prompt templates for the system and assistant.

All prompts enforce:
1. Grounding — only answer from retrieved scheme data
2. Brevity — keep responses short for mobile/WhatsApp
3. Safety — say "I'm not sure" when data is insufficient
4. Language — respond in the user's detected language
5. Code-mixing — mirror the user's style
"""

# ═══════════════════════════════════════════════════════════════════════════
#  System prompt for LLM
# ═══════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are JanKalyan (जनकल्याण), a helpful government welfare scheme assistant for India.

STRICT RULES:
1. You ONLY answer questions about government welfare schemes.
2. You ONLY use the scheme data provided to you in the context. NEVER make up eligibility criteria, documents, or benefits.
3. If the provided scheme data does not contain the answer, say: "मुझे इसकी पक्की जानकारी नहीं है। कृपया आधिकारिक वेबसाइट देखें।" (or the equivalent in the user's language)
4. Keep responses SHORT (under 150 words). Users are on mobile phones with limited data.
5. Use very simple language. Avoid English jargon when responding in Hindi/Tamil.
6. Respond in the SAME language the user writes in.
7. If the user writes in mixed Hindi-English (code-mixing like "mera aadhaar kho gaya"), respond in the same mixed style.
8. Format document lists as numbered items for easy reading.
9. Always include the official website link when recommending a scheme.
10. Never discuss politics, make promises about approval, or guarantee eligibility.
11. If asked about something outside welfare schemes, politely redirect.
12. For Aadhaar-related questions, guide the user to uidai.gov.in.

RESPONSE FORMAT for scheme recommendations:
📋 *Scheme Name*
✅ Why it may fit you: [brief reason]
📄 Documents needed:
1. [doc1]
2. [doc2]
🔗 Official site: [url]

If multiple schemes match, list each one separately in this format."""


# ═══════════════════════════════════════════════════════════════════════════
#  LLM extraction prompt — used to parse ambiguous user inputs
# ═══════════════════════════════════════════════════════════════════════════

EXTRACT_PROMPT = """Extract the {field} from the following user input. The input may be in Hindi, Tamil, English, or code-mixed.

User input: "{user_input}"

Rules:
- For "state": Return the Indian state name in English (e.g., "Uttar Pradesh", "Tamil Nadu", "Madhya Pradesh"). If unclear, return "unknown".
- For "occupation": Return exactly one of: farmer, laborer, student, homemaker, artisan, other. If they mention farming/kisan/agriculture → farmer. If they mention work/mazdoor/labour → laborer. If they mention craft/weaving/pottery → artisan.
- For "gender": Return exactly one of: male, female, other.
- For "age": Return just the number.
- For "income_band": Return exactly one of: low, medium, high. (low = under 10000, medium = 10000-25000, high = above 25000)

Return ONLY the extracted value, nothing else. No explanation."""


# ═══════════════════════════════════════════════════════════════════════════
#  Eligibility question templates (trilingual)
# ═══════════════════════════════════════════════════════════════════════════

QUESTIONS = {
    "greeting": {
        "en": "🙏 Welcome to *JanKalyan* — your welfare scheme assistant!\n\nI'll ask you a few simple questions to find government schemes you may be eligible for.\n\nWhich *state* do you live in?",
        "hi": "🙏 *जनकल्याण* में आपका स्वागत है!\n\nमैं आपसे कुछ सवाल पूछूंगा ताकि आपके लिए सरकारी योजनाएं खोज सकूं।\n\nआप किस *राज्य* में रहते हैं?",
        "ta": "🙏 *ஜனகல்யாண்* க்கு வரவேற்கிறோம்!\n\nஉங்களுக்கான அரசு திட்டங்களைக் கண்டறிய சில கேள்விகள் கேட்கிறேன்.\n\nநீங்கள் எந்த *மாநிலத்தில்* வசிக்கிறீர்கள்?",
    },
    "age": {
        "en": "How old are you? (Just the number)",
        "hi": "आपकी उम्र कितनी है? (सिर्फ नंबर बताएं)",
        "ta": "உங்கள் வயது என்ன? (எண் மட்டும்)",
    },
    "gender": {
        "en": "Your gender?\n1️⃣ Male\n2️⃣ Female\n3️⃣ Other",
        "hi": "आपका लिंग?\n1️⃣ पुरुष\n2️⃣ महिला\n3️⃣ अन्य",
        "ta": "உங்கள் பாலினம்?\n1️⃣ ஆண்\n2️⃣ பெண்\n3️⃣ பிற",
    },
    "occupation": {
        "en": "What is your occupation?\n1️⃣ Farmer\n2️⃣ Laborer/Worker\n3️⃣ Student\n4️⃣ Homemaker\n5️⃣ Artisan/Craftsman\n6️⃣ Other",
        "hi": "आपका पेशा क्या है?\n1️⃣ किसान\n2️⃣ मजदूर/श्रमिक\n3️⃣ छात्र/विद्यार्थी\n4️⃣ गृहिणी\n5️⃣ कारीगर/शिल्पकार\n6️⃣ अन्य",
        "ta": "உங்கள் தொழில் என்ன?\n1️⃣ விவசாயி\n2️⃣ தொழிலாளி\n3️⃣ மாணவர்\n4️⃣ இல்லத்தரசி\n5️⃣ கைவினைஞர்\n6️⃣ பிற",
    },
    "income": {
        "en": "What is your household's monthly income?\n1️⃣ Less than ₹10,000\n2️⃣ ₹10,000 – ₹25,000\n3️⃣ More than ₹25,000",
        "hi": "आपके परिवार की मासिक आय कितनी है?\n1️⃣ ₹10,000 से कम\n2️⃣ ₹10,000 – ₹25,000\n3️⃣ ₹25,000 से अधिक",
        "ta": "உங்கள் குடும்பத்தின் மாத வருமானம் என்ன?\n1️⃣ ₹10,000 க்கும் குறைவு\n2️⃣ ₹10,000 – ₹25,000\n3️⃣ ₹25,000 க்கும் அதிகம்",
    },
    "existing_benefits": {
        "en": "Are you already receiving any government benefits?\n1️⃣ No, none\n2️⃣ Yes, ration card / BPL\n3️⃣ Yes, pension\n4️⃣ Yes, other scheme\n5️⃣ Not sure",
        "hi": "क्या आप पहले से कोई सरकारी लाभ ले रहे हैं?\n1️⃣ नहीं, कोई नहीं\n2️⃣ हां, राशन कार्ड / BPL\n3️⃣ हां, पेंशन\n4️⃣ हां, अन्य योजना\n5️⃣ पता नहीं",
        "ta": "நீங்கள் ஏற்கனவே ஏதேனும் அரசு உதவி பெறுகிறீர்களா?\n1️⃣ இல்லை\n2️⃣ ஆம், ரேஷன் கார்டு / BPL\n3️⃣ ஆம், ஓய்வூதியம்\n4️⃣ ஆம், வேறு திட்டம்\n5️⃣ தெரியவில்லை",
    },
    "results_header": {
        "en": "🎯 Based on your details, here are schemes you may be eligible for:\n",
        "hi": "🎯 आपकी जानकारी के आधार पर, ये योजनाएं आपके लिए हो सकती हैं:\n",
        "ta": "🎯 உங்கள் விவரங்களின் அடிப்படையில், நீங்கள் தகுதி பெறக்கூடிய திட்டங்கள்:\n",
    },
    "no_results": {
        "en": "😔 Sorry, I couldn't find matching schemes based on your information.\n\nPlease check https://www.myscheme.gov.in for all available schemes, or type *reset* to try again with different details.",
        "hi": "😔 माफ करें, आपकी जानकारी के आधार पर मुझे कोई योजना नहीं मिली।\n\nकृपया https://www.myscheme.gov.in पर सभी योजनाएं देखें, या *reset* टाइप करके फिर से कोशिश करें।",
        "ta": "😔 மன்னிக்கவும், உங்கள் தகவல்களின் அடிப்படையில் பொருந்தும் திட்டங்கள் கிடைக்கவில்லை.\n\nhttps://www.myscheme.gov.in இல் அனைத்து திட்டங்களையும் பார்க்கவும், அல்லது *reset* டைப் செய்து மீண்டும் முயற்சிக்கவும்.",
    },
    "ask_more": {
        "en": "\n\n💬 Want to know more about any scheme? Type the scheme name or ask a question.\n📋 Type *checklist* to get a document checklist you can save.\n🔄 Type *reset* to start over.",
        "hi": "\n\n💬 किसी योजना के बारे में और जानना चाहते हैं? योजना का नाम लिखें या कोई सवाल पूछें।\n📋 *checklist* लिखें दस्तावेज़ चेकलिस्ट के लिए।\n🔄 *reset* लिखें फिर से शुरू करने के लिए।",
        "ta": "\n\n💬 ஏதேனும் திட்டத்தைப் பற்றி மேலும் தெரிந்துகொள்ள விரும்புகிறீர்களா? திட்டத்தின் பெயரை டைப் செய்யுங்கள்.\n📋 *checklist* டைப் செய்யுங்கள் ஆவண பட்டியலுக்கு.\n🔄 மீண்டும் தொடங்க *reset* டைப் செய்யுங்கள்.",
    },
    "unknown": {
        "en": "🤔 I'm not sure about that. I can only help with government welfare schemes.\n\nType *reset* to start finding schemes, or ask about a specific scheme like PM-KISAN or Ayushman Bharat.",
        "hi": "🤔 मुझे इसके बारे में पक्की जानकारी नहीं है। मैं केवल सरकारी योजनाओं में मदद कर सकता हूँ।\n\n*reset* लिखें योजनाएं खोजने के लिए, या PM-KISAN या आयुष्मान भारत जैसी योजना के बारे में पूछें।",
        "ta": "🤔 இது பற்றி எனக்கு உறுதியான தகவல் இல்லை. அரசு நலத்திட்டங்களில் மட்டுமே உதவ முடியும்.\n\n*reset* டைப் செய்து திட்டங்களைக் கண்டறியுங்கள், அல்லது PM-KISAN அல்லது ஆயுஷ்மான் பாரத் போன்ற திட்டத்தைப் பற்றி கேளுங்கள்.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  RAG prompt — grounded scheme Q&A
# ═══════════════════════════════════════════════════════════════════════════

RAG_PROMPT_TEMPLATE = """You are JanKalyan, a government welfare scheme assistant. Answer the user's question ONLY based on the official scheme data below.

SCHEME DATA:
{scheme_data}

USER QUESTION: {question}

RULES:
- Respond in {language}. If the user writes in code-mixed Hindi-English, respond the same way.
- Keep it under 150 words.
- Use very simple language (rural user with low literacy).
- If the answer is NOT in the scheme data above, say clearly: "मुझे इसकी पक्की जानकारी नहीं है। कृपया आधिकारिक वेबसाइट पर जांचें।" (or equivalent in {language})
- Always include the official website URL.
- Format document lists as numbered items.
- Never invent eligibility criteria, amounts, or dates not present in the data."""
