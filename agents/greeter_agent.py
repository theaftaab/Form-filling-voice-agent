# agents/greeter_agent.py
"""
Greeter Agent - simplified version that works with the current LiveKit structure
"""

import logging
from typing import Annotated
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from pydantic import Field

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
                "You are a helpful and friendly government service assistant for Karnataka. "
                "Have natural conversations with users - don't sound robotic or like a telecaller. "
                "Listen to what users need and help them accordingly. "
                "If their request relates to general inquiries, complaints, feedback, or contacting a department, use the contact form. "
                "If they need tree cutting permissions, forest clearances, or felling transit permits, use the felling form. "
                "If their request doesn't match these services, politely explain you can't help with that specific issue. "
                "Always be conversational and helpful, not mechanical."
            ),
            # llm=openai.LLM(model="gpt-4o-mini", parallel_tool_calls=False),
            # tts=openai.TTS(voice="alloy"),
            # tools=[
            #     self.set_language,
            #     self.to_contact_form,
            #     self.to_felling_form,
            #     self.detect_intent,
            # ],
        )

    async def on_enter(self):
        await super().on_enter()
        userdata = self.session.userdata
        userdata.agent_type = "greeter"

        if not userdata.language_selected:
            await self.session.say(
                "Hello! I'm here to help you with Karnataka Forest services. "
                "Would you prefer to continue in English or Kannada?"
            )
        else:
            await self._ask_for_service_intent(userdata.preferred_language)

    async def _ask_for_service_intent(self, language):
        """Ask what service the user needs"""
        messages = {
            "english": (
                "Great! How can I help you today? Just tell me what you need - "
                "whether it's a general inquiry, complaint, or if you need permission for tree cutting. "
                "What brings you here?"
            ),
            "kannada": (
                "ಇಂದು ನಾನು ನಿಮಗೆ ಯಾವ ರೀತಿಯಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು?"
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

    @function_tool()
    async def detect_intent(
        self,
        user_request: Annotated[str, Field(description="What the user is asking for or needs help with")],
    ) -> str:
        """Called when the user explains what they need help with."""
        request_lower = user_request.lower()
        userdata = self.session.userdata
        
        # Contact form - general inquiries, complaints, feedback, department contact
        contact_keywords = [
            'complaint', 'complain', 'feedback', 'inquiry', 'inquire', 'question', 'ask',
            'contact', 'reach', 'speak', 'talk', 'department', 'office', 'help', 'support',
            'information', 'details', 'know', 'find out', 'general', 'service', 'problem',
            'issue', 'concern', 'suggestion', 'request', 'application status', 'status'
        ]
        
        # Felling form - tree cutting, forest permissions
        felling_keywords = [
            'tree', 'trees', 'cut', 'cutting', 'fell', 'felling', 'remove', 'removal',
            'forest', 'wood', 'timber', 'permission', 'permit', 'clearance', 'transit',
            'transport', 'move', 'chop', 'harvest', 'logging'
        ]
        
        # Check for contact form intent
        if any(keyword in request_lower for keyword in contact_keywords):
            agent, message = await self.to_contact_form()
            if userdata.preferred_language == "kannada":
                return "ಸರಿ, ನಾನು ನಿಮಗೆ ಸಂಪರ್ಕ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ."
            return "I understand you need to contact a department or make an inquiry. Let me help you with the contact form."
        
        # Check for felling form intent  
        if any(keyword in request_lower for keyword in felling_keywords):
            agent, message = await self.to_felling_form()
            if userdata.preferred_language == "kannada":
                return "ಸರಿ, ನಾನು ನಿಮಗೆ ಮರ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ."
            return "I understand you need tree cutting permission. Let me help you with the felling transit permission form."
        
        # If no match, politely decline
        if userdata.preferred_language == "kannada":
            return "ಕ್ಷಮಿಸಿ, ನಾನು ಆ ವಿಷಯದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ. ನಾನು ಕೇವಲ ಸಾಮಾನ್ಯ ವಿಚಾರಣೆಗಳು ಮತ್ತು ಮರ ಕಡಿಯುವ ಅನುಮತಿಗಳಿಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ."
        return "I'm sorry, I can't help you with that specific request. I can only assist with general inquiries and tree cutting permissions. Is there anything else I can help you with in these areas?"