# JanKalyan (जनकल्याण) — AI Welfare Scheme Chatbot

**Live Demo:** [https://jankalyan-chatbot.onrender.com](https://jankalyan-chatbot.onrender.com)

**AI-based multilingual chatbot for Indian welfare scheme awareness.**

Helps rural beneficiaries discover government schemes they're eligible for, in Hindi, Tamil, and English — including code-mixed input.

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment (optional)
```bash
cp .env.example .env
# Edit .env with your API keys (optional — works without them)
```

### 3. Seed the database
```bash
python seed_db.py
```

### 4. Run the server
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Open the chat UI
Visit **http://localhost:8000** in your browser.

---

## 🏗️ Architecture

```
WhatsApp Cloud API ──▶ FastAPI Backend ──▶ SQLite (10 schemes)
                          │
Web Chat Simulator ──────▶│
                          │
                    ┌─────┴─────┐
                    │ Convo FSM │ ←─ Language Detector
                    │ Retrieval │ ←─ Rule-based Matching
                    │ LLM/Tmpl  │ ←─ Sarvam Mayura (optional)
                    └───────────┘
```

## 🌐 Supported Languages
- **English**
- **Hindi** (हिन्दी)
- **Tamil** (தமிழ்)
- **Code-mixed** (e.g., "मेरा aadhaar खो गया")

## 📋 Covered Schemes
1. PM-KISAN
2. Ayushman Bharat (PM-JAY)
3. PMAY (Pradhan Mantri Awas Yojana)
4. Ujjwala Yojana
5. MGNREGA
6. Sukanya Samriddhi Yojana
7. Atal Pension Yojana
8. PM Vishwakarma
9. Kisan Credit Card (KCC)
10. Ladli Behna Yojana (Madhya Pradesh)

## 🔑 API Keys (Optional)

| Key | Purpose | Required? |
|-----|---------|-----------|
| `SARVAM_API_KEY` | Natural language responses via Mayura LLM + translation | No — uses templates |
| `WHATSAPP_TOKEN` | WhatsApp Cloud API | No — use web simulator |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp sender | No |
| `WEBHOOK_VERIFY_TOKEN` | WhatsApp webhook verification | No |

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/ -v

# Manual test via API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test1", "message": "नमस्ते"}'
```

## 🐳 Docker

```bash
docker build -t jankalyan .
docker run -p 8000:8000 jankalyan
```

## ☁️ Deploy to Render

We have included a `render.yaml` file for easy deployment as a background worker or web service.

1. Push this code to GitHub.
2. In the Render Dashboard, click **New+** -> **Blueprint**.
3. Connect your repository. Render will automatically detect the `render.yaml` file.
4. Set the `SARVAM_API_KEY` and WhatsApp tokens in the Render Environment Variables tab if you want to test those integrations.
5. Deploy! The service will use Docker to build and run automatically.

## 📁 Project Structure

```
├── app/
│   ├── main.py           # FastAPI routes
│   ├── config.py         # Environment config
│   ├── models.py         # Data models
│   ├── conversation.py   # Chat state machine
│   ├── language.py       # Language detection
│   ├── retrieval.py      # Eligibility matching
│   ├── llm.py            # LLM + template formatter
│   ├── prompts.py        # Prompt templates
│   ├── whatsapp.py       # WhatsApp Cloud API
│   ├── schemes_data.py   # 10 scheme records
│   └── db.py             # SQLite + FTS5
├── web/                  # Chat simulator UI
├── tests/                # Test suite
├── seed_db.py            # DB seeder
├── Dockerfile
└── requirements.txt
```

## 📜 License

Built for hackathon demonstration purposes. Scheme data sourced from official government websites.
