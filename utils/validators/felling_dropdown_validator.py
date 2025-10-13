def validate_dropdown(field_name: str, value: str) -> bool:
    """Validate dropdown-based fields using hardcoded values from frontend."""
    value_clean = value.strip().lower()

    AREA_TYPES = ["urban area", "rural area"]
    DISTRICTS = [
        "bagalkote", "ballari (bellary)", "belagavi (belgaum)", "bengaluru rural",
        "bengaluru urban", "bidar", "chamarajanagar", "chikkaballapur",
        "chikkamagaluru (chikmagalur)", "chitradurga", "dakshina kannada",
        "davanagere", "dharwad", "gadag", "hassan", "haveri",
        "kalaburagi (gulbarga)", "kodagu (coorg)", "kolar", "koppal", "mandya",
        "mysuru (mysore)", "raichur", "ramanagara", "shivamogga (shimoga)",
        "tumakuru (tumkur)", "udupi", "uttara kannada (karwar)",
        "vijayapura (bijapur)", "yadgir"
    ]
    APPLICANT_TYPES = ["individual", "entity", "gpa holder"]
    YES_NO = ["yes", "no"]
    YES_NO_NA = ["yes", "no", "not applicable"]

    if field_name == "in_area_type":
        return value_clean in AREA_TYPES
    elif field_name == "district":
        return value_clean in DISTRICTS
    elif field_name == "applicant_type":
        return value_clean in APPLICANT_TYPES
    elif field_name in [
        "boundary_demarcated",
        "tree_reserved_to_gov",
    ]:
        return value_clean in YES_NO
    elif field_name in ["unconditional_consent", "license_enclosed"]:
        return value_clean in YES_NO_NA
    else:
        return True  # skip validation for non-dropdown fields