# agents/felling_agent.py
"""
Felling Form Agent - complete working version
"""
from utils.validators.felling_dropdown_validator import validate_dropdown
import logging
from typing import Annotated
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from pydantic import Field
from livekit.plugins import soniox
from agents.base_agent import BaseFormAgent
from utils.frontend import send_to_frontend
import regex as re
logger = logging.getLogger(__name__)


class FellingFormAgent(BaseFormAgent):
    """
    Conversational agent for Tree Felling Permission Form.
    """

    def __init__(self, language: str = "en") -> None:
        super().__init__(
            instructions=(
                # English rules
                "You are a form-filling assistant for the Karnataka Forest Department Tree Felling Permission form. "
                "You MUST collect information strictly one field at a time using the provided tool functions. "
                "Never skip fields, never summarize prematurely, and never ask for multiple fields together. "
                "The exact order is:\n"
                "1. in_area_type → district → taluk → village → khata_number → survey_number → total_extent_acres → guntas → anna\n"
                "2. applicant_type → applicant_name → father_name → address → applicant_district → applicant_taluk → pincode → mobile_number → email_id\n"
                "3. tree_species → tree_age → tree_girth\n"
                "4. east → west → north → south\n"
                "5. purpose_of_felling → boundary_demarcated → tree_reserved_to_gov → unconditional_consent → license_enclosed → agree_terms\n"
                "At the end, always call confirm_and_submit_felling_form(). "
                "⚠️ Never jump ahead. Always wait for user input before moving to the next field.\n\n"

                # Kannada rules
                "ನೀವು ಕರ್ನಾಟಕ ಅರಣ್ಯ ಇಲಾಖೆಯ ಮರ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್ ಅನ್ನು ಭರ್ತಿ ಮಾಡಲು ಸಹಾಯ ಮಾಡುವ ಸಹಾಯಕನಾಗಿದ್ದೀರಿ. "
                "ಪ್ರತಿ ಹಂತವನ್ನು ಒಂದೊಂದು ಬಾರಿ ಮಾತ್ರ ಕೇಳಬೇಕು. "
                "ಒಂದೇ ಸಮಯದಲ್ಲಿ ಹಲವಾರು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಬಾರದು, ಯಾವುದನ್ನೂ ಬಿಡಬಾರದು. "
                "ಕಡ್ಡಾಯ ಕ್ರಮ:\n"
                "1. ಪ್ರದೇಶದ ಪ್ರಕಾರ → ಜಿಲ್ಲೆ → ತಾಲೂಕು → ಗ್ರಾಮ → ಖಾತೆ ಸಂಖ್ಯೆ → ಸರ್ವೇ ಸಂಖ್ಯೆ → ಒಟ್ಟು ಎಕರೆ → ಗುಂಟೆ → ಅಣ್ಣಾ\n"
                "2. ಅರ್ಜಿದಾರರ ಪ್ರಕಾರ → ಅರ್ಜಿದಾರರ ಹೆಸರು → ತಂದೆಯ ಹೆಸರು → ವಿಳಾಸ → ಅರ್ಜಿದಾರರ ಜಿಲ್ಲೆ → ಅರ್ಜಿದಾರರ ತಾಲೂಕು → ಪಿನ್ ಕೋಡ್ → ಮೊಬೈಲ್ ಸಂಖ್ಯೆ → ಇಮೇಲ್ ಐಡಿ\n"
                "3. ಮರದ ಪ್ರಭೇದ → ಮರದ ವಯಸ್ಸು → ಮರದ ಸುತ್ತಳತೆ\n"
                "4. ಪೂರ್ವ ಗಡಿ → ಪಶ್ಚಿಮ ಗಡಿ → ಉತ್ತರ ಗಡಿ → ದಕ್ಷಿಣ ಗಡಿ\n"
                "5. ಕಡಿಯುವ ಉದ್ದೇಶ → ಗಡಿ ಗುರುತು ಮಾಡಿದ್ದೀರಾ → ಮರ ಸರ್ಕಾರಕ್ಕೆ ಮೀಸಲಾಗಿದೆಯೇ → ನಿರ್ವಿಘ್ನ ಅನುಮತಿ → ಪರವಾನಗಿ ಲಗತ್ತಿಸಿದ್ದೀರಾ → ನಿಯಮ/ಷರತ್ತುಗಳನ್ನು ಒಪ್ಪುತ್ತೀರಾ\n"
                "ಕೊನೆಯಲ್ಲಿ ಸದಾ confirm_and_submit_felling_form() ಅನ್ನು ಕರೆ ಮಾಡಬೇಕು. "
                "⚠️ ಪ್ರತಿ ಹಂತಕ್ಕೆ ಬಳಕೆದಾರರ ಉತ್ತರ ಬಂದ ಬಳಿಕ ಮಾತ್ರ ಮುಂದಿನ ಹಂತಕ್ಕೆ ಹೋಗಿ."
            ),
            stt=soniox.STT(params=soniox.STTOptions(
                language_hints=[language],
                context=(
                    "Karnataka Forest Department Tree Felling Permission Form. "
                    "This is a structured form-filling assistant. "
                    "The user will provide **one field at a time** in either Kannada or English. "
                    "Expected field types:\n"
                    "- Location: district, taluk, village, khata number, survey number. "
                    "- Land size: acres, guntas, anna. "
                    "- Applicant details: applicant type (individual/institution), name, father name, address, pincode. "
                    "- Contact details: mobile number (spoken as digits or words), email ID (e.g., gmail.com, yahoo.com, outlook.com). "
                    "- Tree details: species (teak, rosewood, neem, honge, etc.), tree age (in years), tree girth (in cm). "
                    "- Boundaries: east, west, north, south. "
                    "- Other: purpose of felling, boundary demarcated (yes/no), reserved to govt (yes/no), unconditional consent (yes/no), license enclosed (yes/no), agree to terms (yes/no).\n\n"

                    "⚠️ Rules for recognition:\n"
                    "1. Always return numbers as **digits**, not words (e.g., 'ಎಂಟು' or 'eight' → '8'). "
                    "2. For phone numbers, output as continuous digits without spaces. "
                    "3. For pincodes, output as exactly 6 digits. "
                    "4. For khata/survey numbers, preserve alphanumeric values exactly. "
                    "5. For email IDs, capture them literally (e.g., 'example at gmail dot com' → 'example@gmail.com'). "
                    "6. Recognize common Kannada/English synonyms: "
                    "   - acres → ಏಕರೆ, guntas → ಗುಂಟೆ, anna → ಅಣ್ಣಾ. "
                    "   - pincode → ಪಿನ್ ಕೋಡ್, khata → ಖಾತೆ, survey → ಸರ್ವೇ. "
                    "7. Do not summarize — transcribe exactly what was spoken. "
                    "8. This is not open conversation, it is **form data capture**. "
                    "9. Prioritize Kannada legal/administrative terms when spoken.\n\n"

                    "Bias phrases: khata number, survey number, pincode, applicant type, mobile number, email ID, "
                    "tree species, acres, guntas, anna, boundary demarcated, unconditional consent, reserved to government."
                    "ಕರ್ನಾಟಕ ಅರಣ್ಯ ಇಲಾಖೆಯ ವೃಕ್ಷ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್. "
                    "ಇದು ಒಂದು ಸಂಯೋಜಿತ (structured) ಫಾರ್ಮ್-ಫಿಲ್ಲಿಂಗ್ ಸಹಾಯಕ. "
                    "ಬಳಕೆದಾರರು **ಒಂದೇ ಸಮಯದಲ್ಲಿ ಒಂದು ಕ್ಷೇತ್ರ (field)** ಅನ್ನು ಕನ್ನಡ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಒದಗಿಸುತ್ತಾರೆ. "
                    "ನಿರೀಕ್ಷಿಸಲಾದ ಕ್ಷೇತ್ರಗಳ ಪ್ರಕಾರ:\n"
                    "- ಸ್ಥಳ: ಜಿಲ್ಲೆ, ತಾಲೂಕು, ಗ್ರಾಮ, ಖಾತೆ ಸಂಖ್ಯೆ, ಸರ್ವೇ ಸಂಖ್ಯೆ. "
                    "- ಭೂಮಿಯ ಗಾತ್ರ: ಎಕರೆ, ಗುಂಟೆ, ಅಣ್ಣಾ. "
                    "- ಅರ್ಜಿದಾರರ ವಿವರಗಳು: ಅರ್ಜಿದಾರರ ಪ್ರಕಾರ (ವೈಯಕ್ತಿಕ/ಸಂಸ್ಥೆ), ಹೆಸರು, ತಂದೆಯ ಹೆಸರು, ವಿಳಾಸ, ಪಿನ್‌ಕೋಡ್. "
                    "- ಸಂಪರ್ಕ ವಿವರಗಳು: ಮೊಬೈಲ್ ಸಂಖ್ಯೆ (ಅಂಕೆಗಳಾಗಿ ಅಥವಾ ಪದಗಳಲ್ಲಿ), ಇಮೇಲ್ ಐಡಿ (ಉದಾ: gmail.com, yahoo.com, outlook.com). "
                    "- ಮರದ ವಿವರಗಳು: ಪ್ರಭೇದಗಳು (ಟೀಕ್, ರೋಸ್‌ವುಡ್, ಬೇವು, ಹೊಂಗೆ ಇತ್ಯಾದಿ), ಮರದ ವಯಸ್ಸು (ವರ್ಷಗಳಲ್ಲಿ), ಮರದ ಸುತ್ತಳತೆ (ಸೆಂ.ಮೀ.). "
                    "- ಗಡಿಗಳು: ಪೂರ್ವ, ಪಶ್ಚಿಮ, ಉತ್ತರ, ದಕ್ಷಿಣ. "
                    "- ಇತರೆ: ಕಡಿಯುವ ಉದ್ದೇಶ, ಗಡಿ ಗುರುತು ಮಾಡಿದ್ದೀರಾ (ಹೌದು/ಇಲ್ಲ), ಸರ್ಕಾರಕ್ಕೆ ಮೀಸಲಾಗಿದೆಯೇ (ಹೌದು/ಇಲ್ಲ), ನಿರ್ವಿಘ್ನ ಅನುಮತಿ (ಹೌದು/ಇಲ್ಲ), ಪರವಾನಗಿ ಲಗತ್ತಿಸಿದ್ದೀರಾ (ಹೌದು/ಇಲ್ಲ), ನಿಯಮ/ಷರತ್ತುಗಳನ್ನು ಒಪ್ಪುತ್ತೀರಾ (ಹೌದು/ಇಲ್ಲ).\n\n"

                    "⚠️ ಗುರುತಿಸುವ ನಿಯಮಗಳು:\n"
                    "1. ಯಾವಾಗಲೂ ಸಂಖ್ಯೆಗಳನ್ನು **ಅಂಕೆಗಳಾಗಿ** (digits) ಹಿಂತಿರುಗಿಸಿ, ಪದಗಳಾಗಿ ಬೇಡ (ಉದಾ: 'ಎಂಟು' ಅಥವಾ 'eight' → '8'). "
                    "2. ಮೊಬೈಲ್ ಸಂಖ್ಯೆಗಳು — ಯಾವುದೇ ಖಾಲಿ ಜಾಗವಿಲ್ಲದೆ ನಿರಂತರ ಅಂಕೆಗಳಾಗಿ ಬರೆಯಬೇಕು. "
                    "3. ಪಿನ್‌ಕೋಡ್ — ಕಡ್ಡಾಯವಾಗಿ 6 ಅಂಕೆಗಳಾಗಿರಬೇಕು. "
                    "4. ಖಾತೆ/ಸರ್ವೇ ಸಂಖ್ಯೆ — ಅಕ್ಷರ-ಅಂಕೆ (alphanumeric) ಮೌಲ್ಯವನ್ನು ಅಚ್ಚುಕಟ್ಟಾಗಿ ಉಳಿಸಬೇಕು. "
                    "5. ಇಮೇಲ್ ಐಡಿಗಳು — ಶಬ್ದರೂಪವನ್ನು ನೇರವಾಗಿ ಸೆರೆಹಿಡಿಯಿರಿ (ಉದಾ: 'example at gmail dot com' → 'example@gmail.com'). "
                    "6. ಸಾಮಾನ್ಯ ಕನ್ನಡ/ಇಂಗ್ಲಿಷ್ ಸಮಾನಾರ್ಥಕ ಪದಗಳನ್ನು ಗುರುತಿಸಬೇಕು: "
                    "   - ಎಕರೆ → acres, ಗುಂಟೆ → guntas, ಅಣ್ಣಾ → anna. "
                    "   - ಪಿನ್ ಕೋಡ್ → pincode, ಖಾತೆ → khata, ಸರ್ವೇ → survey. "
                    "7. ಸಾರಾಂಶ ಮಾಡಬೇಡಿ — ನಿಖರವಾಗಿ ಮಾತನಾಡಿದುದನ್ನು ಬರೆಯಿರಿ. "
                    "8. ಇದು ಮುಕ್ತ ಸಂಭಾಷಣೆ ಅಲ್ಲ, ಇದು **ಫಾರ್ಮ್ ಡೇಟಾ ಸೆರೆಹಿಡಿಯುವ ಪ್ರಕ್ರಿಯೆ**. "
                    "9. ಬಳಸಿದರೆ ಕನ್ನಡದ ಕಾನೂನು/ನಿರ್ವಹಣಾ ಪದಗಳಿಗೆ ಹೆಚ್ಚಿನ ಆದ್ಯತೆ ನೀಡಿ.\n\n"

                    "ಭೇದಗೊಳಿಸಬೇಕಾದ ಪದಗಳು (Bias phrases): ಖಾತೆ ಸಂಖ್ಯೆ, ಸರ್ವೇ ಸಂಖ್ಯೆ, ಪಿನ್‌ಕೋಡ್, ಅರ್ಜಿದಾರರ ಪ್ರಕಾರ, ಮೊಬೈಲ್ ಸಂಖ್ಯೆ, ಇಮೇಲ್ ಐಡಿ, "
                    "ಮರದ ಪ್ರಭೇದ, ಎಕರೆ, ಗುಂಟೆ, ಅಣ್ಣಾ, ಗಡಿ ಗುರುತು, ನಿರ್ವಿಘ್ನ ಅನುಮತಿ, ಸರ್ಕಾರಕ್ಕೆ ಮೀಸಲು."
                )
            ),
            ))
        

    async def on_enter(self):
        await super().on_enter()
        userdata = self.session.userdata
        userdata.agent_type = "felling"

        # 🚀 Always start the form flow
        await self._start_form_collection()



    async def _start_form_collection(self):
        userdata = self.session.userdata
        if userdata.preferred_language == "kannada":
            await self.session.say(
                "ನಮಸ್ಕಾರ! ವೃಕ್ಷ ಕಡಿಯುವ ಅನುಮತಿ ಫಾರ್ಮ್‌ಗಾಗಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ದಯವಿಟ್ಟು ಸ್ಥಳದ ಪ್ರಕಾರವನ್ನು ಹೇಳಿ (ಉದಾ: ಅರಣ್ಯ, ಖಾಸಗಿ ಭೂಮಿ, ಆದಾಯ ಭೂಮಿ).")
        else:
            await self.session.say(
                "Hello! I'll help you with the Tree Felling Permission form. Please tell me the type of area (e.g., forest, private land, revenue land).")

    # ---------------- Section 1: Location ----------------

    @function_tool()
    async def update_in_area_type(self, in_area_type: Annotated[str, Field(description="Type of area")]) -> str:
        userdata = self.session.userdata
        if not validate_dropdown("in_area_type", in_area_type):
            if userdata.preferred_language == "kannada":
                return "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಪ್ರದೇಶದ ವಿಧವನ್ನು ನಮೂದಿಸಿ (ಉದಾ: ನಗರ ಪ್ರದೇಶ ಅಥವಾ ಗ್ರಾಮೀಣ ಪ್ರದೇಶ)."
            return "Please select a valid area type (Urban Area or Rural Area)."

        userdata.felling_form.in_area_type = in_area_type
        await send_to_frontend(userdata.ctx.room, {"inAreaType": in_area_type}, topic="formUpdate")
        return "ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು?" if userdata.preferred_language == "kannada" else "Which district is the land located in?"

    @function_tool()
    async def update_district(self, district: Annotated[str, Field(description="District name in English or Kannada")]) -> str:
        userdata = self.session.userdata
        
        # English to Kannada district mapping
        district_mapping = {
            # English: Kannada
            "Bagalkote": "ಬಾಗಲಕೋಟೆ",
            "Ballari (Bellary)": "ಬಳ್ಳಾರಿ",
            "Belagavi (Belgaum)": "ಬೆಳಗಾವಿ",
            "Bengaluru Rural": "ಬೆಂಗಳೂರು ಗ್ರಾಮೀಣ",
            "Bengaluru Urban": "ಬೆಂಗಳೂರು ನಗರ",
            "Bidar": "ಬೀದರ್",
            "Chamarajanagar": "ಚಾಮರಾಜನಗರ",
            "Chikkaballapur": "ಚಿಕ್ಕಬಳ್ಳಾಪುರ",
            "Chikkamagaluru (Chikmagalur)": "ಚಿಕ್ಕಮಗಳೂರು",
            "Chitradurga": "ಚಿತ್ರದುರ್ಗ",
            "Dakshina Kannada": "ದಕ್ಷಿಣ ಕನ್ನಡ",
            "Davanagere": "ದಾವಣಗೆರೆ",
            "Dharwad": "ಧಾರವಾಡ",
            "Gadag": "ಗದಗ",
            "Hassan": "ಹಾಸನ",
            "Haveri": "ಹಾವೇರಿ",
            "Kalaburagi (Gulbarga)": "ಕಲಬುರಗಿ",
            "Kodagu (Coorg)": "ಕೊಡಗು",
            "Kolar": "ಕೋಲಾರ",
            "Koppal": "ಕೊಪ್ಪಳ",
            "Mandya": "ಮಂಡ್ಯ",
            "Mysuru (Mysore)": "ಮೈಸೂರು",
            "Raichur": "ರಾಯಚೂರು",
            "Ramanagara": "ರಾಮನಗರ",
            "Shivamogga (Shimoga)": "ಶಿವಮೊಗ್ಗ",
            "Tumakuru (Tumkur)": "ತುಮಕೂರು",
            "Udupi": "ಉಡುಪಿ",
            "Uttara Kannada (Karwar)": "ಉತ್ತರ ಕನ್ನಡ",
            "Vijayapura (Bijapur)": "ವಿಜಾಪುರ",
            "Yadgir": "ಯಾದಗಿರಿ"
        }

        # Create a reverse mapping (Kannada to English)
        kannada_to_english = {v: k for k, v in district_mapping.items()}

        # Check if input is in English or Kannada
        normalized_input = district.strip()
        is_kannada = any(char in ['ಀ', 'ಁ', 'ಂ', 'ಃ', '಄', 'ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ'] for char in normalized_input)

        # Check if the input matches any district (case-insensitive)
        matched_district = None
        if is_kannada:
            # Check against Kannada names
            for kannada_name, english_name in district_mapping.items():
                if normalized_input.lower() == kannada_name.lower():
                    matched_district = english_name
                    break
        else:
            # Check against English names (with or without parentheses)
            for english_name in district_mapping.keys():
                # Remove text in parentheses for matching
                base_name = re.sub(r'\s*\([^)]*\)', '', english_name).lower()
                if (normalized_input.lower() == english_name.lower() or 
                    normalized_input.lower() == base_name.lower()):
                    matched_district = english_name
                    break

        if not matched_district:
            if userdata.preferred_language == "kannada":
                return "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಜಿಲ್ಲೆಯ ಹೆಸರನ್ನು ನಮೂದಿಸಿ. ಉದಾಹರಣೆ: ಬೆಂಗಳೂರು ನಗರ ಅಥವಾ Bengaluru Urban"
            return "Please enter a valid district name. Example: Bengaluru Urban or ಬೆಂಗಳೂರು ನಗರ"
        if not validate_dropdown("district", matched_district):
            if userdata.preferred_language == "kannada":
                return "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಜಿಲ್ಲೆಯ ಹೆಸರನ್ನು ನಮೂದಿಸಿ."
            return "Please select a valid district from the list."
        # Store the standardized English district name
        userdata.felling_form.district = matched_district
        await send_to_frontend(userdata.ctx.room, {"district": matched_district}, topic="formUpdate")

        # Get next question in appropriate language
        if userdata.preferred_language == "kannada":
            return "ನಿಮ್ಮ ತಾಲೂಕು ಯಾವುದು?"
        return "Which taluk?"

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
    async def update_khata_number(
            self,
            khata_number: Annotated[str, Field(description="Khata number, must be numeric only")]
    ) -> str:
        """Validate and store khata number (only digits allowed)."""
        userdata = self.session.userdata

        # ✅ Strip whitespace
        khata_number_clean = khata_number.strip()

        # ✅ Enforce numeric only
        if not re.fullmatch(r"\d+", khata_number_clean):
            if userdata.preferred_language == "kannada":
                return "ದಯವಿಟ್ಟು ಅಂಕೆಗಳಲ್ಲೇ ಖಾತಾ ಸಂಖ್ಯೆ ನಮೂದಿಸಿ (ಉದಾ: 12345)."
            return "Please enter a valid numeric Khata number (e.g., 12345)."

        # ✅ Store in userdata
        userdata.felling_form.khata_number = khata_number_clean

        # ✅ Notify frontend
        await send_to_frontend(
            userdata.ctx.room,
            {"khata_number": khata_number_clean},
            topic="formUpdate"
        )

        # ✅ Next step
        if userdata.preferred_language == "kannada":
            return "ಸರ್ವೇ ಸಂಖ್ಯೆ ಏನು?"
        return "What is the survey number?"

    @function_tool()
    async def update_survey_number(self, survey_number: Annotated[str, Field(description="Survey number")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.survey_number = survey_number
        await send_to_frontend(userdata.ctx.room, {"survey_number": survey_number}, topic="formUpdate")
        return "ಒಟ್ಟು ಎಕರೆ ಎಷ್ಟು?" if userdata.preferred_language == "kannada" else "What is the total extent in acres?"

    @function_tool()
    async def update_total_extent_acres(self,
                                        acres: Annotated[str, Field(description="Total extent in acres")]) -> str:
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
        if not validate_dropdown("applicant_type", applicant_type):
            if userdata.preferred_language == "kannada":
                return "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಅರ್ಜಿದಾರರ ವಿಧವನ್ನು ನಮೂದಿಸಿ (ವೈಯಕ್ತಿಕ / ಸಂಸ್ಥೆ / ಜಿಪಿಎ ಧಾರಕ)."
            return "Please select a valid applicant type (Individual / Entity / GPA Holder)."

        userdata.felling_form.applicant_type = applicant_type
        await send_to_frontend(userdata.ctx.room, {"applicantType": applicant_type}, topic="formUpdate")
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
    async def update_applicant_district(self, applicant_district: Annotated[
        str, Field(description="Applicant district")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.applicant_district = applicant_district
        await send_to_frontend(userdata.ctx.room, {"applicant_district": applicant_district}, topic="formUpdate")
        return "ಅರ್ಜಿದಾರರ ತಾಲೂಕು ಯಾವುದು?" if userdata.preferred_language == "kannada" else "Which is your applicant taluk?"

    @function_tool()
    async def update_applicant_taluk(self,
                                     applicant_taluk: Annotated[str, Field(description="Applicant taluk")]) -> str:
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
    async def update_email_id(
            self,
            email: Annotated[str, Field(description="Email ID provided by the user")]
    ) -> str:
        """Validate, store, and confirm user's email ID"""
        userdata = self.session.userdata

        # ✅ Clean up input
        email_clean = email.strip()

        # ✅ Basic email regex check
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(email_pattern, email_clean):
            if userdata.preferred_language == "kannada":
                return "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಇಮೇಲ್ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿ."
            return "Please provide a valid email address."

        # ✅ Store in userdata
        userdata.felling_form.email_id = email_clean

        # ✅ Notify frontend
        await send_to_frontend(
            userdata.ctx.room,
            {"email_id": email_clean},
            topic="formUpdate"
        )

        # ✅ Confirm back to user + next prompt
        if userdata.preferred_language == "kannada":
            return f"ನಿಮ್ಮ ಇಮೇಲ್ ವಿಳಾಸ {email_clean} ಉಳಿಸಲಾಗಿದೆ. ಯಾವ ಮರವನ್ನು ಕಡಿಯಲು ಬಯಸುತ್ತೀರಿ?"
        return f"Your email {email_clean} has been saved. What tree species do you want to fell?"

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
    async def update_purpose_of_felling(self,
                                        purpose: Annotated[str, Field(description="Purpose of felling")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.purpose_of_felling = purpose
        await send_to_frontend(userdata.ctx.room, {"purpose_of_felling": purpose}, topic="formUpdate")
        return "ಭೂಮಿಯ ಗಡಿ ಗುರುತು ಮಾಡಿದ್ದೀರಾ?" if userdata.preferred_language == "kannada" else "Is the boundary demarcated?"

    @function_tool()
    async def update_applicant_type(self, applicant_type: Annotated[str, Field(description="Applicant type")]) -> str:
        userdata = self.session.userdata
        if not validate_dropdown("applicant_type", applicant_type):
            if userdata.preferred_language == "kannada":
                return "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಅರ್ಜಿದಾರರ ವಿಧವನ್ನು ನಮೂದಿಸಿ (ವೈಯಕ್ತಿಕ / ಸಂಸ್ಥೆ / ಜಿಪಿಎ ಧಾರಕ)."
            return "Please select a valid applicant type (Individual / Entity / GPA Holder)."

        userdata.felling_form.applicant_type = applicant_type
        await send_to_frontend(userdata.ctx.room, {"applicantType": applicant_type}, topic="formUpdate")
        return "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?" if userdata.preferred_language == "kannada" else "What is your full name?"

    @function_tool()
    async def update_tree_reserved_to_gov(self,
                                          val: Annotated[str, Field(description="Tree reserved to govt?")]) -> str:
        userdata = self.session.userdata
        userdata.felling_form.tree_reserved_to_gov = val
        await send_to_frontend(userdata.ctx.room, {"tree_reserved_to_gov": val}, topic="formUpdate")
        return "ನಿರ್ವಿಘ್ನ ಅನುಮತಿ ಇದೆಯೇ?" if userdata.preferred_language == "kannada" else "Is unconditional consent given?"

    @function_tool()
    async def update_unconditional_consent(self,
                                           val: Annotated[str, Field(description="Unconditional consent?")]) -> str:
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
