# handlers/session.py
import logging
from livekit.agents.voice import AgentSession
from models.userdata import UserData

logger = logging.getLogger(__name__)


def create_session(ctx, userdata: UserData) -> AgentSession:
    """
    Create and configure an AgentSession for the current room.
    """
    session = AgentSession(
        ctx=ctx,
        userdata=userdata,
        # optional: you can pass initial agent=None and switch later
    )

    logger.info("🎧 AgentSession created successfully")
    return session