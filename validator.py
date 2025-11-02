# ===============================
# CLASS: VALIDATOR
# ===============================

import unicodedata
import string


class Validator:
    """
    Utility class responsible for checking data quality:
    - Detecting null or empty values
    - Detecting non-ASCII or invisible characters
    """

    def __init__(self):
        self.invalid_users = []  # Keep invalid or suspicious users

    # -------------------------------
    # BASIC VALIDATION
    # -------------------------------

    @staticmethod
    def _is_valid_value(value) -> bool:
        """
        Recursively checks whether a given value is valid.
        Valid means: not None, not empty, not a blank string.
        Works for nested dicts and lists.
        """
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, dict):
            return all(Validator._is_valid_value(v) for v in value.values())
        if isinstance(value, list):
            return all(Validator._is_valid_value(v) for v in value)
        return True

    # -------------------------------
    # CHARACTER VALIDATION
    # -------------------------------

    @staticmethod
    def contains_strange_characters(text: str) -> bool:
        """
        Checks if the given string contains any non-ASCII
        or invisible Unicode characters.
        """
        if not isinstance(text, str):
            return False

        for char in text:
            # Skip normal printable ASCII characters
            if char in string.printable:
                continue

            # Detect non-printable or control Unicode categories
            category = unicodedata.category(char)
            if category.startswith(("C", "Z")):  # C = control chars, Z = separators
                return True

            # Detect non-ASCII characters
            if ord(char) > 127:
                return True

        return False

    @staticmethod
    def _iterate_fields(data, parent_key=""):
        """
        Recursively iterate through all nested fields of a dictionary
        and yield (key_path, value) pairs.
        Example: ('location.city', 'Paris')
        """
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
        - Keep invalid users in memory for review.
        """
        valid_users = []
        strange_count = 0
        self.invalid_users = []

        for i, user in enumerate(users):
            # Check for missing or invalid values
            if not self._is_valid_value(user):
                self.invalid_users.append(user)
                continue

            # Detect strange characters
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
