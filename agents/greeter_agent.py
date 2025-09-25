# agents/greeter_agent.py
"""
Greeter Agent - simplified version that works with the current LiveKit structure
"""

import logging
from livekit.agents.llm import function_tool
from livekit.plugins import openai

from agents.base_agent import BaseAgent
from utils.frontend import send_to_frontend

logger = logging.getLogger(__name__)


class GreeterAgent(BaseAgent):
    """
    Entry point agent.
    Handles greeting, language selection, and routing to other agents.
    """

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a friendly receptionist for the Karnataka Government services. "
                "Your job is to greet users, help them select their language (English or Kannada), "
                "and understand what service they need. Guide them to the right service: "
                "- 'Contact Form' for general inquiries and communication "
                "- 'Felling Transit Permission' for tree cutting permissions "
                "Use the appropriate transfer tools based on their request."
            ),
            llm=openai.LLM(model="gpt-4o-mini", parallel_tool_calls=False),
            tts=openai.TTS(voice="alloy"),
            # tools=[
            #     # ✅ keep set_language from BaseAgent (not duplicated anywhere else)
            #     # self.set_language,
            #     self.to_contact_form,
            #     self.to_felling_form,
            # ],
        )

    async def on_enter(self):
        await super().on_enter()
        userdata = self.session.userdata
        userdata.agent_type = "greeter"

        if not userdata.language_selected:
            await self.session.say(
                "Hello! Welcome to Karnataka Government services. "
                "Please select your preferred language - English or Kannada?"
            )
        else:
            await self._ask_for_service_intent(userdata.preferred_language)

    async def _ask_for_service_intent(self, language):
        """Ask what service the user needs"""
        messages = {
            "english": (
                "How can I help you today? I can assist you with: "
                "- Contact Form for general inquiries "
                "- Felling Transit Permission for tree cutting permits "
                "What would you like to do?"
            ),
            "kannada": (
                "ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು? ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ: "
                "- ಸಾಮಾನ್ಯ ವಿಚಾರಣೆಗಳಿಗಾಗಿ ಸಂಪರ್ಕ ಫಾರ್ಮ್ "
                "- ಮರ ಕತ್ತರಿಸುವ ಪರವಾನಗಿಗಾಗಿ ಫೆಲ್ಲಿಂಗ್ ಟ್ರಾನ್ಸಿಟ್ ಪರ್ಮಿಷನ್ "
                "ನೀವು ಏನು ಮಾಡಲು ಬಯಸುತ್ತೀರಿ?"
            ),
        }
        message = messages.get((language or "").lower(), messages["english"])
        await self.session.say(message)

    @function_tool()
    async def to_contact_form(self) -> tuple:
        """Called when user wants to fill a contact form for general inquiries."""
        userdata = self.session.userdata
        userdata.requested_route = "/contact-form"

        # ✅ Correct send_to_frontend usage
        await send_to_frontend(
            userdata.ctx.room,
            {"route": userdata.requested_route},
            topic="navigation"
        )

        return await self._transfer_to_agent("contact")
        # same for felling

    @function_tool()
    async def to_felling_form(self) -> tuple:
        """Called when user wants to fill a felling transit permission form."""
        userdata = self.session.userdata
        userdata.requested_route = "/felling-transit-permission"

        # ✅ Correct send_to_frontend usage
        await send_to_frontend(
            userdata.ctx.room,
            {"route": userdata.requested_route},
            topic="navigation"
        )

        return await self._transfer_to_agent("felling")