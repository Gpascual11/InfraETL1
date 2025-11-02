# ===============================
# CLASS 2: TRANSFORMER
# ===============================

import statistics
from collections import Counter
from validator import Validator


class Transformer:
    """
    The Transformer class is responsible for:
      - Validating and cleaning user data
      - Removing or flagging invalid entries
      - Generating descriptive statistics
      - Computing additional derived metrics (e.g., password strength)
    """

    def __init__(self, users: list):
        # Raw user data extracted from API
        self.users = users
        # List to store any invalid or suspicious users (for audit/review)
        self.invalid_users = []

    # -------------------------------
    # DATA VALIDATION
    # -------------------------------

    def validate_data(self):
        """
        Perform full data integrity validation:
          - Removes users with missing/null values
          - Detects fields containing strange or invisible characters
        Keeps invalid users in self.invalid_users for later inspection.
        """
        print("Validating data integrity...")

        valid_users = []

        for idx, user in enumerate(self.users, start=1):
            # Step 1: Skip user entirely if it contains empty or null values
            if not Validator.is_valid_value(user):
                self.invalid_users.append(user)
                continue

            # Step 2: Check each text field for unwanted characters
            has_strange = False
            for key, value in self._iterate_fields(user):
                if isinstance(value, str) and Validator.contains_strange_characters(value):
                    print(f"Strange character detected in user #{idx}, field '{key}': {value}")
                    has_strange = True

            # Step 3: Store user appropriately
            if has_strange:
                # Keep flagged users for manual review but exclude from valid dataset
                self.invalid_users.append(user)
            else:
                valid_users.append(user)

        # Update internal list of clean users
        self.users = valid_users

        print(f"Validation complete. {len(self.invalid_users)} records flagged for review.")

    # -------------------------------
    # HELPER: FIELD ITERATOR
    # -------------------------------

    def _iterate_fields(self, data, parent_key=""):
        """
        Recursively iterate through all nested fields of a dictionary or list.
        Produces a (field_path, value) tuple for each terminal field.
        Example:
            input: {"location": {"country": "Germany"}}
            yields: ("location.country", "Germany")
        """
        if isinstance(data, dict):
            # Dive into nested dictionaries
            for k, v in data.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                yield from self._iterate_fields(v, full_key)
        elif isinstance(data, list):
            # Enumerate list items (e.g., address lines, phone numbers)
            for i, item in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                yield from self._iterate_fields(item, full_key)
        else:
            # Base case: reached a single scalar field
            yield (parent_key, data)

    # -------------------------------
    # STATISTICS GENERATION
    # -------------------------------

    def generate_stats(self) -> dict:
        """
        Generate descriptive statistics for the cleaned dataset:
          - Count of total users
          - Average, min, and max age
          - Most frequent gender
          - Number of unique countries represented
        Returns:
            dict: containing summary metrics.
        """
        print("Generating statistics...")

        # Extract values efficiently using list comprehensions
        ages = [user["dob"]["age"] for user in self.users if "dob" in user and "age" in user["dob"]]
        genders = [user["gender"] for user in self.users if "gender" in user]
        countries = [user["location"]["country"] for user in self.users if "location" in user]

        stats = {
            "total_users": len(self.users),
            "average_age": round(statistics.mean(ages), 2) if ages else 0,
            "minimum_age": min(ages) if ages else 0,
            "maximum_age": max(ages) if ages else 0,
            "most_frequent_gender": Counter(genders).most_common(1)[0][0] if genders else None,
            "different_countries": len(set(countries)),
        }

        return stats

    # -------------------------------
    # PASSWORD STRENGTH ANALYSIS
    # -------------------------------

    def calculate_password_strength_stats(self):
        """
        Compute password strength metrics across all users.

        Rules:
          - A 'strong' password is defined as having >10 characters
          - Other passwords are considered 'weak'

        Returns:
            dict: {
                "strong": count of strong passwords,
                "weak": count of weak passwords,
                "percent_strong": percentage of strong passwords,
                "total_users": total count considered
            }
        """
        total = len(self.users)
        if total == 0:
            # Avoid division by zero
            return {"strong": 0, "weak": 0, "percent_strong": 0, "total_users": 0}

        # Count strong passwords
        strong = 0
        for user in self.users:
            password = user.get("login", {}).get("password", "")
            if isinstance(password, str) and len(password) > 10:
                strong += 1

        # Compute percentages
        percent_strong = round((strong / total) * 100, 2)

        return {
            "strong": strong,
            "weak": total - strong,
            "percent_strong": percent_strong,
            "total_users": total
        }

    # -------------------------------
    # GETTER
    # -------------------------------

    def get_users(self) -> list:
        """
        Return the list of validated and cleaned user records.
        Used by the Loader for output.
        """
        return self.users
