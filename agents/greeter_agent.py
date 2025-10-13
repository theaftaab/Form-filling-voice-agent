# agents/greeter_agent.py
"""
Greeter Agent - simplified version that works with the current LiveKit structure
"""

import logging
from typing import Annotated
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from pydantic import Field
import json
from livekit.agents.llm import LLM, ChatMessage
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
            llm=openai.LLM(model="gpt-4o-mini", parallel_tool_calls=False),
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

        # Set Kannada as default language if not already set
        if not userdata.language_selected:
            userdata.preferred_language = "kannada"
            userdata.language_selected = True
            await self._ask_for_service_intent("kannada")
        else:
            await self._ask_for_service_intent(userdata.preferred_language)

    async def _ask_for_service_intent(self, language):
        """Ask what service the user needs"""
        userdata = self.session.userdata
        userdata.preferred_language = (language or "english").lower()  # ✅ persist

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
        message = messages.get(userdata.preferred_language, messages["english"])
        await self.session.say(message)

    @function_tool()
    async def set_language(
            self,
            language: Annotated[str, Field(description="User's preferred language: english or kannada")]
    ) -> str:
        """Store the user's preferred language in session userdata."""
        userdata = self.session.userdata
        userdata.preferred_language = language.lower()
        userdata.language_selected = True

        if userdata.preferred_language == "kannada":
            return "ಸರಿ, ನಾವು ಕನ್ನಡದಲ್ಲಿ ಮುಂದುವರೆಯೋಣ."
        return "Okay, we'll continue in English."

    @function_tool()
    async def to_contact_form(self) -> str:
        """Called when user wants to fill a contact form for general inquiries."""
        userdata = self.session.userdata
        userdata.requested_route = "/contact-form"

        # ✅ Send route update to frontend
        await send_to_frontend(
            userdata.ctx.room,
            {"route": userdata.requested_route},
            topic="navigation"
        )

        # ✅ Switch agent
        await self.switch_agent("contact")

        # ✅ Return a message (not the tuple)
        if userdata.preferred_language == "kannada":
            return "ಸರಿ, ನಾನು ನಿಮಗೆ ಸಂಪರ್ಕ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ."
        return "Okay, let me switch you to the contact form."

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

        return await self._transfer_to_agent("felling", language=userdata.preferred_language or "english")

    @function_tool()
    async def detect_intent(
            self,
            user_request: Annotated[str, Field(description="What the user is asking for or needs help with")],
    ) -> str:
        """Classify the user request into one of: contact, felling, unknown."""

        prompt = f"""
        You are an intent classifier for Karnataka government services.
        Classify the following request into exactly one category:
        - "contact" → general inquiries, complaints, feedback, department contact
        - "felling" → tree cutting, felling, transit permission, forest clearance
        - "unknown" → anything else

        Respond ONLY in JSON format, no extra text:
        {{
          "intent": "contact" | "felling" | "unknown"
        }}

        Request: "{user_request}"
        """

        try:
            resp = await self.llm.chat([ChatMessage(role="user", content=prompt)])
            result = json.loads(resp.content.strip())
            intent = result.get("intent", "unknown").lower()
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            intent = "unknown"

        userdata = self.session.userdata

        # Route based on intent
        if intent == "contact":
            return await self.to_contact_form()

        elif intent == "felling":
            return await self.to_felling_form()

        else:
            if userdata.preferred_language == "kannada":
                return "ಕ್ಷಮಿಸಿ, ನಾನು ಆ ವಿಷಯದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ. ನಾನು ಕೇವಲ ಸಾಮಾನ್ಯ ವಿಚಾರಣೆಗಳು ಮತ್ತು ಮರ ಕಡಿಯುವ ಅನುಮತಿಗಳಿಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ."
            return "I'm sorry, I can't help with that specific request. I can only assist with general inquiries and tree cutting permissions."