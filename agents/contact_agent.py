# agents/contact_agent.py
"""
Contact Form Agent - minimal working version
"""

import logging
from typing import Annotated
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from pydantic import Field

from agents.base_agent import BaseFormAgent
from utils.frontend import send_to_frontend

logger = logging.getLogger(__name__)


class ContactFormAgent(BaseFormAgent):
    """
    Conversational agent for Contact Form.
    """

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a friendly voice assistant for the Karnataka Government Contact Form. "
                "Your job is to collect the following information step by step: "
                "1. Organization/Department name "
                "2. Subject of inquiry "
                "3. Phone number "
                "4. Message/inquiry details "
                "After collecting all fields, ask for confirmation and then call confirm_and_submit_contact_form(). "
            ),
            # llm=openai.LLM(model="gpt-4o-mini"),
            # tts=openai.TTS(voice="alloy"),
            # tools=[
            #     self.to_greeter,
            #     self.set_language,
            #     self.update_company,
            #     self.update_subject,
            #     self.update_phone,
            #     self.update_message,
            #     self.confirm_and_submit_contact_form,
            # ],
        )

    async def on_enter(self):
        await super().on_enter()
        userdata = self.session.userdata
        userdata.agent_type = "contact"

    async def _start_form_collection(self):
        """Start collecting contact form data"""
        userdata = self.session.userdata
        if userdata.preferred_language == "kannada":
            await self.session.say("ನಮಸ್ಕಾರ! ಸಂಪರ್ಕ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಲು ನಾನು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ನಿಮ್ಮ ಸಂಸ್ಥೆ ಅಥವಾ ಇಲಾಖೆಯ ಹೆಸರು ಏನು?")
        else:
            await self.session.say("Hello! I'll help you fill out the contact form. What's your organization or department name?")

    @function_tool()
    async def update_company(
        self,
        company: Annotated[str, Field(description="The user's organization or department name")],
    ) -> str:
        userdata = self.session.userdata
        userdata.contact_form.company = company
        await send_to_frontend(userdata.ctx.room, {"company": company}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ವಿಷಯ ಏನು?"
        else:
            return "What's the subject of your inquiry?"

    @function_tool()
    async def update_subject(
        self,
        subject: Annotated[str, Field(description="The subject of the inquiry")],
    ) -> str:
        userdata = self.session.userdata
        userdata.contact_form.subject = subject
        await send_to_frontend(userdata.ctx.room, {"subject": subject}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ನಿಮ್ಮ ಫೋನ್ ಸಂಖ್ಯೆ ಏನು?"
        else:
            return "What's your phone number?"

    @function_tool()
    async def update_phone(
        self,
        phone: Annotated[str, Field(description="The customer's phone number")],
    ) -> str:
        userdata = self.session.userdata
        userdata.contact_form.phone = phone
        await send_to_frontend(userdata.ctx.room, {"phone": phone}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಹೇಳಿ."
        else:
            return "Please tell me your message or inquiry details."

    @function_tool()
    async def update_message(
        self,
        message: Annotated[str, Field(description="The user's message or inquiry details")],
    ) -> str:
        userdata = self.session.userdata
        userdata.contact_form.message = message
        await send_to_frontend(userdata.ctx.room, {"message": message}, topic="formUpdate")
        return await self._ask_for_confirmation()



    @function_tool()
    async def confirm_and_submit_contact_form(self) -> str:
        userdata = self.session.userdata
        
        if not userdata.awaiting_confirmation:
            return "Please provide all required information first."

        # Check for missing fields
        missing_fields = userdata.contact_form.get_missing_fields()
        if missing_fields:
            missing = ", ".join(missing_fields)
            return f"Please provide the following missing information: {missing}"

        userdata.awaiting_confirmation = False
        userdata.should_submit = True
        await send_to_frontend(userdata.ctx.room, {"should_submit": True}, topic="formUpdate", reliable=True)
        
        if userdata.preferred_language == "kannada":
            return "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಸಂದೇಶ ಯಶಸ್ವಿಯಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ."
        else:
            return "Thank you! Your message has been submitted successfully."