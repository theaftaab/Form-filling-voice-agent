from dataclasses import dataclass, field
from typing import Optional, Dict

from livekit.agents import JobContext
from livekit.agents.voice import Agent

from .contact_form import ContactFormData
from .felling_form import FellingFormData


@dataclass
class UserData:
    """
    Session-level state for each user/room.
    Lives for the duration of an agent session.
    """

    # LiveKit context (room/session)
    ctx: Optional[JobContext] = None

    # ------------------------------------------------------------
    # Conversation state
    # ------------------------------------------------------------
    preferred_language: Optional[str] = None   # "english" | "kannada"
    language_selected: bool = False
    awaiting_confirmation: bool = False
    should_submit: bool = False

    # ------------------------------------------------------------
    # Form-specific state
    # ------------------------------------------------------------
    contact_form: ContactFormData = field(default_factory=ContactFormData)
    felling_form: FellingFormData = field(default_factory=FellingFormData)

    # Track which form/service is active: "contact" | "felling" | "greeter"
    agent_type: Optional[str] = None

    # ------------------------------------------------------------
    # Agent navigation
    # ------------------------------------------------------------
    agents: Dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None
    requested_route: Optional[str] = None

    @property
    def current_form(self):
        """Get the currently active form based on agent_type"""
        if self.agent_type == "contact":
            return self.contact_form
        elif self.agent_type == "felling":
            return self.felling_form
        return None