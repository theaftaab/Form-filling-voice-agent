from dataclasses import dataclass, field
from typing import Optional
from .base_form import BaseFormData


@dataclass
class FellingFormData(BaseFormData):
    """
    Data structure for Tree Felling Permission Form.
    Matches the frontend TreeFellingFormData interface.
    """

    # Section 1: Location details
    in_area_type: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None
    khata_number: Optional[str] = None
    survey_number: Optional[str] = None
    total_extent_acres: Optional[str] = None
    guntas: Optional[str] = None
    anna: Optional[str] = None

    # Section 2: Applicant details
    applicant_type: Optional[str] = None
    applicant_name: Optional[str] = None
    father_name: Optional[str] = None
    address: Optional[str] = None
    applicant_district: Optional[str] = None
    applicant_taluk: Optional[str] = None
    pincode: Optional[str] = None
    mobile_number: Optional[str] = None
    email_id: Optional[str] = None

    # Section 3: Tree details
    tree_species: Optional[str] = None
    tree_age: Optional[str] = None
    tree_girth: Optional[str] = None

    # Section 4: Site boundary details
    east: Optional[str] = None
    west: Optional[str] = None
    north: Optional[str] = None
    south: Optional[str] = None

    # Section 5: Other details
    purpose_of_felling: Optional[str] = None
    boundary_demarcated: Optional[str] = None
    tree_reserved_to_gov: Optional[str] = None
    unconditional_consent: Optional[str] = None
    license_enclosed: Optional[str] = None

    # File uploads (only track status: uploaded / not uploaded)
    files_uploaded: dict[str, bool] = field(default_factory=dict)

    # Terms acceptance
    agree_terms: bool = False

    # -----------------------------------------------------------------
    # Validation config (used by BaseFormData)
    # -----------------------------------------------------------------
    required_fields = [
        "in_area_type",
        "district",
        "taluk",
        "village",
        "khata_number",
        "survey_number",
        "total_extent_acres",
        "guntas",
        "anna",
        "applicant_type",
        "applicant_name",
        "father_name",
        "address",
        "applicant_district",
        "applicant_taluk",
        "pincode",
        "mobile_number",
        "tree_species",
        "tree_age",
        "tree_girth",
        "east",
        "west",
        "north",
        "south",
        "purpose_of_felling",
    ]

    required_flags = ["agree_terms"]