# utils/frontend.py
"""
Frontend communication utilities.
Provides helpers for agents to send structured updates to the frontend (React).
All data is published over LiveKit's data channel with JSON payloads.
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Core Sender
# -------------------------------------------------------------------

async def send_to_frontend(room, data: Dict[str, Any], topic: str = "formUpdate", reliable: bool = False):
    """
    Publish structured JSON data to the frontend via LiveKit data channel.
    
    Args:
        room: LiveKit Room instance (server-side).
        data: dict payload to send.
        topic: string topic to categorize data (default "formUpdate").
        reliable: whether delivery must be guaranteed (default False).
    """
    if not room:
        logger.warning("send_to_frontend called with no room instance")
        return

    try:
        payload = json.dumps(data).encode("utf-8")
        await room.local_participant.publish_data(payload, topic=topic, reliable=reliable)
        logger.debug(f"✅ Sent to frontend [{topic}]: {data}")
    except Exception as e:
        logger.error(f"❌ Failed to send data to frontend: {e}")


# -------------------------------------------------------------------
# Convenience Wrappers
# -------------------------------------------------------------------

async def send_field_update(room, field_name: str, value: Any):
    """
    Send an update for a single form field to frontend.
    """
    await send_to_frontend(room, {"field": field_name, "value": value}, topic="formUpdate")


async def send_bulk_update(room, updates: Dict[str, Any]):
    """
    Send multiple fields update to frontend at once.
    Example:
        await send_bulk_update(room, {
            "applicant_name": "Aftaab",
            "village": "Mandya"
        })
    """
    await send_to_frontend(room, updates, topic="formUpdate")


async def trigger_form_submit(room):
    """
    Tell frontend to submit the form (end of flow).
    """
    await send_to_frontend(room, {"should_submit": True}, topic="formUpdate", reliable=True)


async def send_error(room, message: str, code: Optional[str] = None):
    """
    Send error notification to frontend.
    """
    payload = {"error": message}
    if code:
        payload["code"] = code
    await send_to_frontend(room, payload, topic="error", reliable=True)