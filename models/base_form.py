#models/base_form.py
from dataclasses import asdict
from typing import List, Optional

class BaseFormData:
    """
    Abstract base class for all form dataclasses.
    Provides shared validation and serialization helpers.
    """

    # ✅ List of required fields (child classes must override this)
    required_fields: List[str] = []

    # ✅ Optional list of boolean flags (e.g. terms acceptance)
    required_flags: List[str] = []

    def get_missing_fields(self) -> List[str]:
        """
        Returns a list of missing required fields.
        Required fields must be defined in child class.
        """
        missing = []
        for field_name in self.required_fields:
            value = getattr(self, field_name, None)
            if not value:
                missing.append(field_name)

        for flag in self.required_flags:
            if not getattr(self, flag, False):
                missing.append(flag)

        return missing

    def is_complete(self) -> bool:
        """Returns True if all required fields and flags are filled."""
        return len(self.get_missing_fields()) == 0

    def to_dict(self) -> dict:
        """
        Convert form into a dictionary for serialization.
        Uses dataclasses.asdict if available.
        """
        try:
            return asdict(self)  # works for dataclasses
        except Exception:
            # fallback: __dict__
            return self.__dict__

    def update_field(self, field_name: str, value: Optional[str]) -> None:
        """
        Update a field dynamically if it exists.
        Safe setter used when receiving frontend updates.
        """
        if hasattr(self, field_name):
            setattr(self, field_name, value)

    def set_field(self, field_name: str, value: Optional[str]) -> None:
        """
        Alias for update_field - used by data handler.
        """
        self.update_field(field_name, value)