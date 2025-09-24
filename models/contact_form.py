from dataclasses import dataclass
from typing import Optional
from .base_form import BaseFormData


@dataclass
class ContactFormData(BaseFormData):
    """Data structure for the Contact Form fields"""

    company: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    phone: Optional[str] = None

    # ✅ Required fields
    required_fields = ["company", "subject", "message", "phone"]