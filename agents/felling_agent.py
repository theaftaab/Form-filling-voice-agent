# agents/felling_agent.py
"""
Felling Form Agent - minimal working version
"""

import logging
from typing import Annotated
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from pydantic import Field

from agents.base_agent import BaseFormAgent
from utils.frontend import send_to_frontend

logger = logging.getLogger(__name__)


class FellingFormAgent(BaseFormAgent):
    """
    Conversational agent for Tree Felling Permission Form.
    """

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a voice assistant for the Karnataka Forest Department Felling Transit Permission form. "
                "Collect information step by step in this order: "
                "1. Applicant name, 2. Father's name, 3. Mobile number, 4. Address, 5. Village, "
                "6. Taluk, 7. District, 8. Pincode, 9. Tree species, 10. Tree age, 11. Tree girth. "
                "After collecting all fields, ask for confirmation and call confirm_and_submit_felling_form(). "
            ),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=openai.TTS(voice="alloy"),
            # tools=[
            #     self.to_greeter,
            #     self.set_language,
            #     self.update_name,
            #     self.update_father_name,
            #     self.update_mobile,
            #     self.update_address,
            #     self.update_village,
            #     self.update_taluk,
            #     self.update_district,
            #     self.update_pincode,
            #     self.update_tree_species,
            #     self.update_tree_age,
            #     self.update_tree_girth,
            #     self.confirm_and_submit_felling_form,
            # ],
        )

    async def on_enter(self):
        await super().on_enter()
        userdata = self.session.userdata
        userdata.agent_type = "felling"

    async def _start_form_collection(self):
        """Start collecting felling form data"""
        userdata = self.session.userdata
        if userdata.preferred_language == "kannada":
            await self.session.say("ನಮಸ್ಕಾರ! ವೃಕ್ಷ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್‌ಗಾಗಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ.")
        else:
            await self.session.say("Hello! I'll help you with the Tree Felling Permission form. Please speak your complete full name clearly.")

    @function_tool()
    async def update_name(
        self,
        name: Annotated[str, Field(description="The applicant's full name")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.applicant_name = name
        await send_to_frontend(userdata.ctx.room, {"applicant_name": name}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ಚೆನ್ನಾಗಿದೆ. ನಿಮ್ಮ ತಂದೆಯ ಪೂರ್ಣ ಹೆಸರು ಏನು?"
        else:
            return "Great! What's your father's complete full name?"

    @function_tool()
    async def update_father_name(
        self,
        father_name: Annotated[str, Field(description="The applicant's father's name")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.father_name = father_name
        await send_to_frontend(userdata.ctx.room, {"father_name": father_name}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ಚೆನ್ನಾಗಿದೆ. ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಏನು?"
        else:
            return "Thank you! What's your mobile number?"

    @function_tool()
    async def update_mobile(
        self,
        mobile: Annotated[str, Field(description="The applicant's mobile number")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.mobile_number = mobile
        await send_to_frontend(userdata.ctx.room, {"mobile_number": mobile}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ಅದ್ಭುತ! ನಿಮ್ಮ ವಿಳಾಸವನ್ನು ಹೇಳಿ."
        else:
            return "Great! Please tell me your address."

    @function_tool()
    async def update_address(
        self,
        address: Annotated[str, Field(description="The applicant's address")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.address = address
        await send_to_frontend(userdata.ctx.room, {"address": address}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ನಿಮ್ಮ ಗ್ರಾಮದ ಹೆಸರು ಏನು?"
        else:
            return "What's your village name?"

    @function_tool()
    async def update_village(
        self,
        village: Annotated[str, Field(description="The village name")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.village = village
        await send_to_frontend(userdata.ctx.room, {"village": village}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ನಿಮ್ಮ ತಾಲೂಕು ಯಾವುದು?"
        else:
            return "Which taluk are you from?"

    @function_tool()
    async def update_taluk(
        self,
        taluk: Annotated[str, Field(description="The taluk name")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.taluk = taluk
        await send_to_frontend(userdata.ctx.room, {"taluk": taluk}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು?"
        else:
            return "Which district are you from?"

    @function_tool()
    async def update_district(
        self,
        district: Annotated[str, Field(description="The district name")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.district = district
        await send_to_frontend(userdata.ctx.room, {"district": district}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ನಿಮ್ಮ ಪಿನ್ ಕೋಡ್ ಏನು?"
        else:
            return "What's your pincode?"

    @function_tool()
    async def update_pincode(
        self,
        pincode: Annotated[str, Field(description="The 6-digit pincode")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.pincode = pincode
        await send_to_frontend(userdata.ctx.room, {"pincode": pincode}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ಯಾವ ರೀತಿಯ ಮರವನ್ನು ಕಡಿಯಲು ಬಯಸುತ್ತೀರಿ?"
        else:
            return "What type of tree do you want to cut?"

    @function_tool()
    async def update_tree_species(
        self,
        species: Annotated[str, Field(description="The species of tree to be felled")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_species = species
        await send_to_frontend(userdata.ctx.room, {"tree_species": species}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ಮರದ ವಯಸ್ಸು ಎಷ್ಟು ವರ್ಷಗಳು?"
        else:
            return "How old is the tree in years?"

    @function_tool()
    async def update_tree_age(
        self,
        age: Annotated[str, Field(description="The age of the tree in years")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_age = age
        await send_to_frontend(userdata.ctx.room, {"tree_age": age}, topic="formUpdate")
        
        if userdata.preferred_language == "kannada":
            return "ಮರದ ಸುತ್ತಳತೆ ಎಷ್ಟು ಸೆಂಟಿಮೀಟರ್?"
        else:
            return "What's the tree girth in centimeters?"

    @function_tool()
    async def update_tree_girth(
        self,
        girth: Annotated[str, Field(description="The girth of the tree in centimeters")],
    ) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_girth = girth
        await send_to_frontend(userdata.ctx.room, {"tree_girth": girth}, topic="formUpdate")
        return await self._ask_for_confirmation(self)



    @function_tool()
    async def confirm_and_submit_felling_form(self) -> str:
        userdata = self.session.userdata
        
        if not userdata.awaiting_confirmation:
            return "Please provide all required information first."

        # Check for missing required fields
        required_fields = ["applicant_name", "father_name", "mobile_number", "address", "village", "taluk", "district", "pincode", "tree_species", "tree_age", "tree_girth"]
        missing_fields = []
        
        for field in required_fields:
            if not getattr(userdata.felling_form, field, None):
                missing_fields.append(field)
        
        if missing_fields:
            missing = ", ".join(missing_fields)
            if userdata.preferred_language == "kannada":
                return f"ದಯವಿಟ್ಟು ಈ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸಿ: {missing}"
            else:
                return f"Please provide the following missing information: {missing}"

        userdata.awaiting_confirmation = False
        userdata.should_submit = True
        await send_to_frontend(userdata.ctx.room, {"should_submit": True}, topic="formUpdate", reliable=True)
        
        if userdata.preferred_language == "kannada":
            return "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ವೃಕ್ಷ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್ ಯಶಸ್ವಿಯಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ."
        else:
            return "Thank you! Your tree felling permission form has been submitted successfully."