import unicodedata
import re

class Validator:
    """Utility class for validating data and helper methods for ETL."""

    def __init__(self):
        """Initializes the Validator"""
        self.invalid_users = []

    @staticmethod
    def is_valid_value(value) -> bool:
        """Recursively check if a value is not null or empty."""
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, dict):
            return all(Validator.is_valid_value(v) for v in value.values())
        if isinstance(value, list):
            return all(Validator.is_valid_value(v) for v in value)
        return True

    @staticmethod
    def contains_strange_characters(text: str) -> bool:
        """Return True if the string contains invalid/non-Latin/invisible characters."""
        if not isinstance(text, str):
            return False

        normalized = unicodedata.normalize("NFKC", text)

        if (
            re.fullmatch(r"&[a-zA-Z0-9#]+;", normalized)  # HTML entities
            or re.fullmatch(r"^[+-]\d{1,2}:\d{2}$", normalized)  # Timezone offsets
            or re.fullmatch(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", normalized)  # Email
            or re.fullmatch(r"^https?://\S+$", normalized)  # URL
        ):
            return False

        allowed_pattern = re.compile(r"^[\w\s'’‘\-–—.,;:/()@+À-ÿ&]+$", re.UNICODE)
        if allowed_pattern.fullmatch(normalized):
            return False

        for ch in normalized:
            if unicodedata.category(ch).startswith("C"):
                return True

        for ch in normalized:
            if ord(ch) > 591:
                return True

        return False

    @staticmethod
    def iterate_fields(data, parent_key=""):
        """
        Recursively iterate through all nested fields of a dictionary or list.
        Produces (field_path, value) tuples for each terminal value.

        Example:
            input: {"location": {"country": "Germany"}}
            yields: ("location.country", "Germany")
        """
        if isinstance(data, dict):
            for k, v in data.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                yield from Validator.iterate_fields(v, full_key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                yield from Validator.iterate_fields(item, full_key)
        else:
            yield parent_key, data