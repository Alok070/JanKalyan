"""
FastAPI application — main entry point.

Routes:
- GET  /              → Serve web chat simulator
- POST /chat          → Web simulator API
- GET  /webhook       → WhatsApp verification
- POST /webhook       → WhatsApp incoming messages
- GET  /api/schemes   → List all schemes (debug)
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.db import init_db, get_all_schemes
from app.conversation import handle_message, reset_session
from app.whatsapp import verify_webhook, parse_incoming_message, send_whatsapp_message

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="JanKalyan — Welfare Scheme Chatbot",
    description="AI-based multilingual chatbot for Indian welfare scheme awareness",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (web chat UI)
WEB_DIR = Path(__file__).parent.parent / "web"
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    logger.info("Initializing database...")
    init_db()

    # Check if schemes exist, if not suggest seeding
    schemes = get_all_schemes()
    if not schemes:
        logger.warning(
            "No schemes in database! Run 'python seed_db.py' to populate."
        )
    else:
        logger.info(f"Database ready with {len(schemes)} schemes")

    logger.info(f"Sarvam API: {'configured' if settings.sarvam_api_key else 'NOT configured (using templates)'}")
    logger.info(f"WhatsApp: {'configured' if settings.whatsapp_token else 'NOT configured (use web simulator)'}")
    logger.info("JanKalyan is ready! 🚀")


# ---------------------------------------------------------------------------
# Web chat simulator
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_web_ui():
    """Serve the web chat simulator."""
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>JanKalyan API is running. Web UI not found.</h1>")


class ChatRequest(BaseModel):
    user_id: str = "web_user"
    message: str


class ChatResponse(BaseModel):
    reply: str
    language: str = "en"


@app.post("/chat", response_model=ChatResponse)
async def web_chat(req: ChatRequest):
    """Web simulator chat endpoint."""
    reply = await handle_message(req.user_id, req.message)
    return ChatResponse(reply=reply)


# ---------------------------------------------------------------------------
# WhatsApp webhook
# ---------------------------------------------------------------------------
@app.get("/webhook")
async def whatsapp_verify(
    request: Request,
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    """WhatsApp webhook verification."""
    result = verify_webhook(mode or "", token or "", challenge or "")
    if result:
        return Response(content=result, media_type="text/plain")
    return Response(status_code=403)


@app.post("/webhook")
async def whatsapp_incoming(request: Request):
    """Handle incoming WhatsApp messages."""
    body = await request.json()

    phone, text = parse_incoming_message(body)
    if phone and text:
        logger.info(f"Message from {phone}: {text[:100]}")
        reply = await handle_message(phone, text)
        await send_whatsapp_message(phone, reply)

    return JSONResponse(content={"status": "ok"})


# ---------------------------------------------------------------------------
# Debug / utility endpoints
# ---------------------------------------------------------------------------
@app.get("/api/schemes")
async def list_schemes():
    """List all schemes in the database (for debugging)."""
    schemes = get_all_schemes()
    return {"count": len(schemes), "schemes": schemes}


@app.post("/api/reset/{user_id}")
async def reset_user(user_id: str):
    """Reset a user's conversation."""
    reset_session(user_id)
    return {"status": "reset", "user_id": user_id}
