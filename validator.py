# ===============================
# CLASS: VALIDATOR
# ===============================

import unicodedata
import re


class Validator:
    """
    Utility class responsible for checking data quality:
    - Detecting null or empty values
    - Detecting truly invalid (non-Latin/invisible) characters
    - Allowing valid email, URL, timezone, and encoded strings
    """

    def __init__(self):
        self.invalid_users = []

    # -------------------------------
    # BASIC VALIDATION
    # -------------------------------

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

    # -------------------------------
    # CHARACTER VALIDATION
    # -------------------------------

    @staticmethod
    def contains_strange_characters(text: str) -> bool:
        """
        Detect if a string contains unusual or invalid characters.

        Valid characters include:
        - Printable ASCII
        - Latin letters (with accents)
        - Common punctuation (including en/em dash)
        - URLs, emails, timezone offsets, HTML entities
        """

        if not isinstance(text, str):
            return False

        # Normalize composed characters (e.g., é → é)
        normalized = unicodedata.normalize("NFKC", text)

        # Whitelist of known valid structured formats
        if (
                re.fullmatch(r"&[a-zA-Z0-9#]+;", normalized)  # HTML entities
                or re.fullmatch(r"^[+-]\d{1,2}:\d{2}$", normalized)  # Timezone offsets
                or re.fullmatch(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", normalized)  # Emails
                or re.fullmatch(r"^https?://[^\s]+$", normalized)  # URLs
        ):
            return False

        # Allow normal punctuation + Latin-1 Supplement + en/em dash
        allowed_pattern = re.compile(
            r"^[\w\s'’‘\-–—.,;:/()@+À-ÿ&]+$",  # includes – (U+2013) and — (U+2014)
            re.UNICODE,
        )

        if allowed_pattern.fullmatch(normalized):
            return False  # All characters are valid

        # Check for invisible/control Unicode characters
        for ch in normalized:
            category = unicodedata.category(ch)
            # 'C' = control, 'Zs' = non-breaking/invisible spaces
            if category.startswith("C") or category == "Zs":
                return True

        # Reject characters outside the Latin Extended-A/B range
        for ch in normalized:
            if ord(ch) > 591:  # covers most Latin-based languages
                return True

        return False

    @staticmethod
    def _iterate_fields(data, parent_key=""):
        """Yield (key_path, value) pairs from nested dicts/lists."""
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                yield from Validator._iterate_fields(value, new_key)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_key = f"{parent_key}[{index}]"
                yield from Validator._iterate_fields(item, new_key)
        else:
            yield parent_key, data

    # -------------------------------
    # PUBLIC INTERFACE
    # -------------------------------

    def validate_batch(self, users: list) -> list:
        """
        Validate and clean a batch of user records.
        - Remove users with null/empty fields.
        - Print users with strange characters.
        - Keep invalid users separately.
        """
        valid_users = []
        strange_count = 0
        self.invalid_users = []

        for i, user in enumerate(users):
            if not self.is_valid_value(user):
                self.invalid_users.append(user)
                continue

            # Detect truly strange (non-Latin/invisible) characters
            has_strange = False
            for key, value in self._iterate_fields(user):
                if isinstance(value, str) and Validator.contains_strange_characters(value):
                    has_strange = True
                    strange_count += 1
                    print(f"Strange character detected in user #{i + 1}, field '{key}': {value}")

            if has_strange:
                self.invalid_users.append(user)
            else:
                valid_users.append(user)

        if self.invalid_users:
            print(f"Removed {len(self.invalid_users)} invalid users (null, empty, or strange characters).")

        if strange_count > 0:
            print(f"{strange_count} strange character occurrences detected across dataset.")

        return valid_users

    def get_invalid_users(self) -> list:
        """Return the list of users that failed validation."""
        return self.invalid_users
