# handlers/data_handler.py
import json
import logging
from livekit.agents import JobContext
from models.userdata import UserData

logger = logging.getLogger(__name__)


def register_data_handler(ctx: JobContext, userdata: UserData):
    """
    Register handlers for receiving frontend data events.
    """
    from livekit import rtc

    def handle_data(packet: rtc.DataPacket):
        try:
            obj = json.loads(packet.data.decode("utf-8"))
            logger.info(f"received data: {obj}")
            field = obj.get("field")
            value = obj.get("value")
            
            if not field or not value:
                return

            # Map frontend field names to userdata fields based on agent type
            if userdata.agent_type == "contact":
                field_mapping = {
                    "company": "company",
                    "subject": "subject", 
                    "message": "message",
                    "phone": "phone",
                }
                # Update contact form
                if field in field_mapping:
                    setattr(userdata.contact_form, field_mapping[field], value)
                    logger.info(f"Updated contact form {field_mapping[field]}: {value}")
                    
            elif userdata.agent_type == "felling":
                field_mapping = {
                    "applicantName": "applicant_name",
                    "fatherName": "father_name",
                    "address": "address",
                    "village": "village",
                    "taluk": "taluk",
                    "district": "district",
                    "mobileNumber": "mobile_number",
                    "emailId": "email_id",
                    "khataNumber": "khata_number",
                    "surveyNumber": "survey_number",
                    "totalExtentAcres": "total_extent_acres",
                    "guntas": "guntas",
                    "anna": "anna",
                    "treeSpecies": "tree_species",
                    "treeAge": "tree_age",
                    "treeGirth": "tree_girth",
                    "pincode": "pincode",
                }
                # Update felling form
                if field in field_mapping:
                    setattr(userdata.felling_form, field_mapping[field], value)
                    logger.info(f"Updated felling form {field_mapping[field]}: {value}")
            else:
                logger.warning(f"Unknown field for {userdata.agent_type} agent: {field}")
                
        except Exception as e:
            logger.error(f"Failed to parse data packet: {e}")
    
    # Register the handler
    ctx.room.on("data_received", handle_data)