"""
WhatsApp Cloud API integration.

Handles:
- Webhook verification (GET)
- Incoming message parsing (POST)
- Sending text replies
- Message splitting for long responses
"""

import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v18.0"
MAX_WHATSAPP_LENGTH = 4096  # WhatsApp max message length


def verify_webhook(mode: str, token: str, challenge: str) -> str | None:
    """Verify the WhatsApp webhook. Returns the challenge if valid, None otherwise."""
    if mode == "subscribe" and token == settings.webhook_verify_token:
        logger.info("Webhook verified successfully")
        return challenge
    logger.warning(f"Webhook verification failed: mode={mode}, token={token}")
    return None


def parse_incoming_message(body: dict) -> tuple[str | None, str | None]:
    """
    Parse an incoming WhatsApp webhook payload.
    Returns (phone_number, message_text) or (None, None) if not a text message.
    """
    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return None, None

        message = messages[0]
        phone = message.get("from", "")
        msg_type = message.get("type", "")

        if msg_type == "text":
            text = message.get("text", {}).get("body", "")
            return phone, text

        # For non-text messages (image, audio, etc.), return a hint
        return phone, f"[{msg_type} message received — I can only process text messages for now]"

    except (IndexError, KeyError) as e:
        logger.error(f"Failed to parse WhatsApp message: {e}")
        return None, None


async def send_whatsapp_message(to: str, text: str):
    """Send a text message via WhatsApp Cloud API."""
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        logger.warning("WhatsApp not configured — message not sent")
        return

    # Split long messages
    chunks = _split_message(text, MAX_WHATSAPP_LENGTH)

    async with httpx.AsyncClient(timeout=10.0) as client:
        for chunk in chunks:
            try:
                resp = await client.post(
                    f"{GRAPH_API_URL}/{settings.whatsapp_phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {settings.whatsapp_token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "messaging_product": "whatsapp",
                        "to": to,
                        "type": "text",
                        "text": {"body": chunk},
                    },
                )
                resp.raise_for_status()
                logger.info(f"Sent WhatsApp message to {to}: {chunk[:50]}...")
            except Exception as e:
                logger.error(f"Failed to send WhatsApp message: {e}")


def _split_message(text: str, max_len: int) -> list[str]:
    """Split a long message at line boundaries."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            if current:
                chunks.append(current.strip())
            current = line
        else:
            current += "\n" + line if current else line

    if current.strip():
        chunks.append(current.strip())

    return chunks or [text[:max_len]]
