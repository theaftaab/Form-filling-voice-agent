# agents/felling_agent.py
"""
Felling Form Agent - complete working version
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
                "Collect information step by step in this order:\n"
                "Section 1 (Location): in_area_type, district, taluk, village, khata_number, survey_number, "
                "total_extent_acres, guntas, anna. \n"
                "Section 2 (Applicant): applicant_type, applicant_name, father_name, address, applicant_district, "
                "applicant_taluk, pincode, mobile_number, email_id. \n"
                "Section 3 (Tree details): tree_species, tree_age, tree_girth. \n"
                "Section 4 (Site boundary): east, west, north, south. \n"
                "Section 5 (Other details): purpose_of_felling, boundary_demarcated, tree_reserved_to_gov, "
                "unconditional_consent, license_enclosed. \n"
                "Finally: agree_terms. After collecting all fields, ask for confirmation and call confirm_and_submit_felling_form()."
            ),
        )

    async def on_enter(self):
        await super().on_enter()
        userdata = self.session.userdata
        userdata.agent_type = "felling"

        # 🚀 Always start the form flow
        await self._start_form_collection()

    async def _start_form_collection(self):
        userdata = self.session.userdata
        if userdata.preferred_language == "kannada":
            await self.session.say("ನಮಸ್ಕಾರ! ವೃಕ್ಷ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್‌ಗಾಗಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ದಯವಿಟ್ಟು ಸ್ಥಳದ ಪ್ರಕಾರವನ್ನು ಹೇಳಿ (ಉದಾ: ಅರಣ್ಯ, ಖಾಸಗಿ ಭೂಮಿ, ಆದಾಯ ಭೂಮಿ).")
        else:
            await self.session.say("Hello! I'll help you with the Tree Felling Permission form. Please tell me the type of area (e.g., forest, private land, revenue land).")

    # ---------------- Section 1: Location ----------------

    @function_tool()
    async def update_in_area_type(self, in_area_type: Annotated[str, Field(description="Type of area")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.in_area_type = in_area_type
        await send_to_frontend(userdata.ctx.room, {"in_area_type": in_area_type}, topic="formUpdate")
        return "ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು?" if userdata.preferred_language == "kannada" else "Which district is the land located in?"

    @function_tool()
    async def update_district(self, district: Annotated[str, Field(description="District name")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.district = district
        await send_to_frontend(userdata.ctx.room, {"district": district}, topic="formUpdate")
        return "ನಿಮ್ಮ ತಾಲೂಕು ಯಾವುದು?" if userdata.preferred_language == "kannada" else "Which taluk?"

    @function_tool()
    async def update_taluk(self, taluk: Annotated[str, Field(description="Taluk name")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.taluk = taluk
        await send_to_frontend(userdata.ctx.room, {"taluk": taluk}, topic="formUpdate")
        return "ನಿಮ್ಮ ಗ್ರಾಮದ ಹೆಸರು ಏನು?" if userdata.preferred_language == "kannada" else "What is the village name?"

    @function_tool()
    async def update_village(self, village: Annotated[str, Field(description="Village name")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.village = village
        await send_to_frontend(userdata.ctx.room, {"village": village}, topic="formUpdate")
        return "ಖಾತೆ ಸಂಖ್ಯೆ ಏನು?" if userdata.preferred_language == "kannada" else "What is the Khata number?"

    @function_tool()
    async def update_khata_number(self, khata_number: Annotated[str, Field(description="Khata number")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.khata_number = khata_number
        await send_to_frontend(userdata.ctx.room, {"khata_number": khata_number}, topic="formUpdate")
        return "ಸರ್ವೇ ಸಂಖ್ಯೆ ಏನು?" if userdata.preferred_language == "kannada" else "What is the survey number?"

    @function_tool()
    async def update_survey_number(self, survey_number: Annotated[str, Field(description="Survey number")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.survey_number = survey_number
        await send_to_frontend(userdata.ctx.room, {"survey_number": survey_number}, topic="formUpdate")
        return "ಒಟ್ಟು ಎಕರೆ ಎಷ್ಟು?" if userdata.preferred_language == "kannada" else "What is the total extent in acres?"

    @function_tool()
    async def update_total_extent_acres(self, acres: Annotated[str, Field(description="Total extent in acres")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.total_extent_acres = acres
        await send_to_frontend(userdata.ctx.room, {"total_extent_acres": acres}, topic="formUpdate")
        return "ಗುಂಟೆ ಎಷ್ಟು?" if userdata.preferred_language == "kannada" else "How many guntas?"

    @function_tool()
    async def update_guntas(self, guntas: Annotated[str, Field(description="Extent in guntas")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.guntas = guntas
        await send_to_frontend(userdata.ctx.room, {"guntas": guntas}, topic="formUpdate")
        return "ಅಣ್ಣಾ ಎಷ್ಟು?" if userdata.preferred_language == "kannada" else "How many annas?"

    @function_tool()
    async def update_anna(self, anna: Annotated[str, Field(description="Extent in anna")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.anna = anna
        await send_to_frontend(userdata.ctx.room, {"anna": anna}, topic="formUpdate")
        return "ಅರ್ಜಿದಾರರ ಪ್ರಕಾರ ಏನು?" if userdata.preferred_language == "kannada" else "What is the applicant type (e.g., individual, institution)?"

    # ---------------- Section 2: Applicant ----------------

    @function_tool()
    async def update_applicant_type(self, applicant_type: Annotated[str, Field(description="Applicant type")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.applicant_type = applicant_type
        await send_to_frontend(userdata.ctx.room, {"applicant_type": applicant_type}, topic="formUpdate")
        return "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?" if userdata.preferred_language == "kannada" else "What is your full name?"

    @function_tool()
    async def update_applicant_name(self, name: Annotated[str, Field(description="Applicant name")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.applicant_name = name
        await send_to_frontend(userdata.ctx.room, {"applicant_name": name}, topic="formUpdate")
        return "ನಿಮ್ಮ ತಂದೆಯ ಹೆಸರು ಏನು?" if userdata.preferred_language == "kannada" else "What is your father's name?"

    @function_tool()
    async def update_father_name(self, father_name: Annotated[str, Field(description="Father's name")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.father_name = father_name
        await send_to_frontend(userdata.ctx.room, {"father_name": father_name}, topic="formUpdate")
        return "ನಿಮ್ಮ ವಿಳಾಸ ಏನು?" if userdata.preferred_language == "kannada" else "What is your address?"

    @function_tool()
    async def update_address(self, address: Annotated[str, Field(description="Applicant address")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.address = address
        await send_to_frontend(userdata.ctx.room, {"address": address}, topic="formUpdate")
        return "ಅರ್ಜಿದಾರರ ಜಿಲ್ಲೆ ಯಾವುದು?" if userdata.preferred_language == "kannada" else "Which is your applicant district?"

    @function_tool()
    async def update_applicant_district(self, applicant_district: Annotated[str, Field(description="Applicant district")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.applicant_district = applicant_district
        await send_to_frontend(userdata.ctx.room, {"applicant_district": applicant_district}, topic="formUpdate")
        return "ಅರ್ಜಿದಾರರ ತಾಲೂಕು ಯಾವುದು?" if userdata.preferred_language == "kannada" else "Which is your applicant taluk?"

    @function_tool()
    async def update_applicant_taluk(self, applicant_taluk: Annotated[str, Field(description="Applicant taluk")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.applicant_taluk = applicant_taluk
        await send_to_frontend(userdata.ctx.room, {"applicant_taluk": applicant_taluk}, topic="formUpdate")
        return "ಪಿನ್‌ ಕೋಡ್ ಏನು?" if userdata.preferred_language == "kannada" else "What is your pincode?"

    @function_tool()
    async def update_pincode(self, pincode: Annotated[str, Field(description="Pincode")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.pincode = pincode
        await send_to_frontend(userdata.ctx.room, {"pincode": pincode}, topic="formUpdate")
        return "ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಏನು?" if userdata.preferred_language == "kannada" else "What is your mobile number?"

    @function_tool()
    async def update_mobile_number(self, mobile: Annotated[str, Field(description="Mobile number")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.mobile_number = mobile
        await send_to_frontend(userdata.ctx.room, {"mobile_number": mobile}, topic="formUpdate")
        return "ನಿಮ್ಮ ಇಮೇಲ್ ಐಡಿ ಏನು?" if userdata.preferred_language == "kannada" else "What is your email ID?"

    @function_tool()
    async def update_email_id(self, email: Annotated[str, Field(description="Email ID")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.email_id = email
        await send_to_frontend(userdata.ctx.room, {"email_id": email}, topic="formUpdate")
        return "ಯಾವ ಮರವನ್ನು ಕಡಿಯಲು ಬಯಸುತ್ತೀರಿ?" if userdata.preferred_language == "kannada" else "What tree species do you want to fell?"

    # ---------------- Section 3: Tree details ----------------

    @function_tool()
    async def update_tree_species(self, species: Annotated[str, Field(description="Tree species")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_species = species
        await send_to_frontend(userdata.ctx.room, {"tree_species": species}, topic="formUpdate")
        return "ಮರದ ವಯಸ್ಸು ಎಷ್ಟು?" if userdata.preferred_language == "kannada" else "What is the age of the tree?"

    @function_tool()
    async def update_tree_age(self, age: Annotated[str, Field(description="Tree age in years")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_age = age
        await send_to_frontend(userdata.ctx.room, {"tree_age": age}, topic="formUpdate")
        return "ಮರದ ಸುತ್ತಳತೆ ಎಷ್ಟು ಸೆಂ.ಮೀ.?" if userdata.preferred_language == "kannada" else "What is the girth of the tree in cm?"

    @function_tool()
    async def update_tree_girth(self, girth: Annotated[str, Field(description="Tree girth")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_girth = girth
        await send_to_frontend(userdata.ctx.room, {"tree_girth": girth}, topic="formUpdate")
        return "ಭೂಮಿಯ ಪೂರ್ವ ಗಡಿ ಏನು?" if userdata.preferred_language == "kannada" else "What is on the east boundary?"

    # ---------------- Section 4: Site boundaries ----------------

    @function_tool()
    async def update_east(self, east: Annotated[str, Field(description="East boundary")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.east = east
        await send_to_frontend(userdata.ctx.room, {"east": east}, topic="formUpdate")
        return "ಪಶ್ಚಿಮ ಗಡಿ ಏನು?" if userdata.preferred_language == "kannada" else "What is on the west boundary?"

    @function_tool()
    async def update_west(self, west: Annotated[str, Field(description="West boundary")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.west = west
        await send_to_frontend(userdata.ctx.room, {"west": west}, topic="formUpdate")
        return "ಉತ್ತರ ಗಡಿ ಏನು?" if userdata.preferred_language == "kannada" else "What is on the north boundary?"

    @function_tool()
    async def update_north(self, north: Annotated[str, Field(description="North boundary")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.north = north
        await send_to_frontend(userdata.ctx.room, {"north": north}, topic="formUpdate")
        return "ದಕ್ಷಿಣ ಗಡಿ ಏನು?" if userdata.preferred_language == "kannada" else "What is on the south boundary?"

    @function_tool()
    async def update_south(self, south: Annotated[str, Field(description="South boundary")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.south = south
        await send_to_frontend(userdata.ctx.room, {"south": south}, topic="formUpdate")
        return "ಮರವನ್ನು ಕಡಿಯುವ ಉದ್ದೇಶ ಏನು?" if userdata.preferred_language == "kannada" else "What is the purpose of felling?"

    # ---------------- Section 5: Other details ----------------

    @function_tool()
    async def update_purpose_of_felling(self, purpose: Annotated[str, Field(description="Purpose of felling")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.purpose_of_felling = purpose
        await send_to_frontend(userdata.ctx.room, {"purpose_of_felling": purpose}, topic="formUpdate")
        return "ಭೂಮಿಯ ಗಡಿ ಗುರುತು ಮಾಡಿದ್ದೀರಾ?" if userdata.preferred_language == "kannada" else "Is the boundary demarcated?"

    @function_tool()
    async def update_boundary_demarcated(self, val: Annotated[str, Field(description="Boundary demarcated (Yes/No)")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.boundary_demarcated = val
        await send_to_frontend(userdata.ctx.room, {"boundary_demarcated": val}, topic="formUpdate")
        return "ಮರ ಸರ್ಕಾರಕ್ಕೆ ಮೀಸಲಾಗಿದೆಯೇ?" if userdata.preferred_language == "kannada" else "Is the tree reserved to government?"

    @function_tool()
    async def update_tree_reserved_to_gov(self, val: Annotated[str, Field(description="Tree reserved to govt?")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_reserved_to_gov = val
        await send_to_frontend(userdata.ctx.room, {"tree_reserved_to_gov": val}, topic="formUpdate")
        return "ನಿರ್ವಿಘ್ನ ಅನುಮತಿ ಇದೆಯೇ?" if userdata.preferred_language == "kannada" else "Is unconditional consent given?"

    @function_tool()
    async def update_unconditional_consent(self, val: Annotated[str, Field(description="Unconditional consent?")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.unconditional_consent = val
        await send_to_frontend(userdata.ctx.room, {"unconditional_consent": val}, topic="formUpdate")
        return "ಪರವಾನಗಿ ಲಗತ್ತಿಸಿದ್ದೀರಾ?" if userdata.preferred_language == "kannada" else "Is license enclosed?"

    @function_tool()
    async def update_license_enclosed(self, val: Annotated[str, Field(description="License enclosed?")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.license_enclosed = val
        await send_to_frontend(userdata.ctx.room, {"license_enclosed": val}, topic="formUpdate")
        return "ನೀವು ನಿಯಮ ಮತ್ತು ಷರತ್ತುಗಳನ್ನು ಒಪ್ಪುತ್ತೀರಾ?" if userdata.preferred_language == "kannada" else "Do you agree to the terms and conditions?"

    @function_tool()
    async def update_agree_terms(self, agree: Annotated[bool, Field(description="Agree to terms")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.agree_terms = agree
        await send_to_frontend(userdata.ctx.room, {"agree_terms": agree}, topic="formUpdate")
        return await self._ask_for_confirmation()

    # ---------------- Final Confirmation ----------------

    @function_tool()
    async def confirm_and_submit_felling_form(self) -> str:
        userdata = self.session.userdata
        form = userdata.felling_form

        # Check for missing fields & flags
        missing_fields = [f for f in form.required_fields if not getattr(form, f, None)]
        missing_flags = [flag for flag in form.required_flags if not getattr(form, flag, False)]

        if missing_fields or missing_flags:
            missing = ", ".join(missing_fields + missing_flags)
            if userdata.preferred_language == "kannada":
                return f"ದಯವಿಟ್ಟು ಈ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸಿ: {missing}"
            else:
                return f"Please provide the following missing information: {missing}"

        # If nothing missing → mark ready to submit
        userdata.awaiting_confirmation = False
        userdata.should_submit = True
        await send_to_frontend(
            userdata.ctx.room,
            {"should_submit": True},
            topic="formUpdate",
            reliable=True,
        )

        if userdata.preferred_language == "kannada":
            return "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ವೃಕ್ಷ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್ ಯಶಸ್ವಿಯಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ."
        else:
            return "Thank you! Your tree felling permission form has been submitted successfully."
