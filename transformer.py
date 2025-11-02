# ===============================
# CLASS 2: TRANSFORMER
# ===============================

import statistics
from collections import Counter
from validator import Validator


class Transformer:
    """Class responsible for validating and transforming user data, and generating statistics"""

    def __init__(self, users: list):
        self.users = users
        self.invalid_users = []  # Store any removed or suspicious users

    def validate_data(self):
        """
        Check all rows for:
        - Missing or null values
        - Strange (non-ASCII or invisible) characters
        Remove invalid ones, but keep them stored separately.
        """
        print("Validating data integrity...")

        valid_users = []

        for idx, user in enumerate(self.users, start=1):
            # Skip entire user if it has invalid or null values
            if not Validator.is_valid_value(user):
                self.invalid_users.append(user)
                continue

            # Scan all fields for strange characters
            has_strange = False
            for key, value in self._iterate_fields(user):
                if isinstance(value, str) and Validator.contains_strange_characters(value):
                    print(f"Strange character detected in user #{idx}, field '{key}': {value}")
                    has_strange = True

            if has_strange:
                # Keep the user but mark them separately for manual review
                self.invalid_users.append(user)
            else:
                valid_users.append(user)

        self.users = valid_users
        print(f"Validation complete. {len(self.invalid_users)} records flagged for review.")

    def _iterate_fields(self, data, parent_key=""):
        """
        Helper method to recursively iterate over all fields in nested dictionaries/lists.
        Returns tuples of (field_path, value).
        Example: ('location.country', 'Germany')
        """
        if isinstance(data, dict):
            for k, v in data.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                yield from self._iterate_fields(v, full_key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                yield from self._iterate_fields(item, full_key)
        else:
            yield (parent_key, data)

    def generate_stats(self) -> dict:
        """Generate descriptive statistics about the user dataset"""
        print("Generating statistics...")

        ages = [user["dob"]["age"] for user in self.users]
        genders = [user["gender"] for user in self.users]
        countries = [user["location"]["country"] for user in self.users]

        stats = {
            "total_users": len(self.users),
            "average_age": round(statistics.mean(ages), 2) if ages else 0,
            "minimum_age": min(ages) if ages else 0,
            "maximum_age": max(ages) if ages else 0,
            "most_frequent_gender": Counter(genders).most_common(1)[0][0] if genders else None,
            "different_countries": len(set(countries)),
        }
        return stats

    def get_users(self) -> list:
        """Return the cleaned list of valid users"""
        return self.users
