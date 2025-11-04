# ===============================
# CLASS 2: TRANSFORMER
# ===============================

import statistics
from collections import Counter, defaultdict
from CSVHelper import CSVHelper
from validator import Validator
from pathlib import Path
from datetime import datetime


class Transformer:
    """
    Transformer class:
      - Reads users from a CSV or a list of dictionaries
      - Validates and cleans user data
      - Generates descriptive statistics
    """

    def __init__(self, users_input, encryption_key: bytes = None):
        if isinstance(users_input, (str, Path)):
            self.users = CSVHelper.load_csv(users_input, key=encryption_key)
        else:
            self.users = users_input

        self.invalid_users = []

    # -------------------------------
    # DATA VALIDATION
    # -------------------------------
    def validate_data(self):
        """Detect fields containing strange or invisible characters."""
        print("Validating data integrity...")
        valid_users = []

        for idx, user in enumerate(self.users, start=1):
            has_strange = False
            for key, value in Validator.iterate_fields(user):
                if isinstance(value, str) and Validator.contains_strange_characters(value):
                    print(f"Strange character detected in user #{idx}, field '{key}': {value}")
                    has_strange = True
            if has_strange:
                self.invalid_users.append(user)
            else:
                valid_users.append(user)

        self.users = valid_users
        print(f"Validation complete. {len(self.invalid_users)} records flagged for review.")

    # -------------------------------
    # STATISTICS GENERATION
    # -------------------------------
    def generate_stats(self) -> dict:
        """Generate descriptive statistics for cleaned dataset."""
        print("Generating statistics...")

        ages = [int(user["dob"]["age"]) for user in self.users if "dob" in user and "age" in user["dob"]]
        genders = [user["gender"] for user in self.users if "gender" in user]
        countries = [user["location"]["country"] for user in self.users if "location" in user]
        nationalities = [user["nat"] for user in self.users if "nat" in user]
        email_domains = [user["email"].split("@")[-1] for user in self.users if "email" in user]
        username_lengths = [len(user.get("login", {}).get("username", "")) for user in self.users]
        passwords = [user.get("login", {}).get("password", "") for user in self.users]

        # 1. Registration Year
        reg_years = defaultdict(int)
        for user in self.users:
            reg_date_str = user.get("registered", {}).get("date", "")
            if reg_date_str:
                try:
                    reg_year = datetime.fromisoformat(reg_date_str.rstrip("Z")).year
                    reg_years[str(reg_year)] += 1
                except ValueError:
                    continue

        # 2. Timezone
        timezones = Counter(
            user.get("location", {}).get("timezone", {}).get("offset")
            for user in self.users
            if user.get("location", {}).get("timezone", {}).get("offset")
        )

        # 3. Age by decade
        age_decades = defaultdict(int)
        for age in ages:
            decade = (age // 10) * 10
            age_decades[f"{decade}s"] += 1

        # 4. Password length stats (simple stat, kept in Transformer)
        password_lengths = [len(p) for p in passwords if p]

        stats = {
            "total_users": len(self.users),
            "average_age": round(statistics.mean(ages), 2) if ages else 0.0,
            "minimum_age": min(ages) if ages else 0,
            "maximum_age": max(ages) if ages else 0,
            "most_frequent_gender": Counter(genders).most_common(1)[0][0] if genders else None,
            "gender_distribution": dict(Counter(genders)),
            "different_countries": len(set(countries)),
            "users_per_country": dict(Counter(countries)),
            "nationality_distribution": dict(Counter(nationalities)),
            "email_domain_distribution": dict(Counter(email_domains)),
            "username_length_stats": {
                "min": min(username_lengths) if username_lengths else 0,
                "max": max(username_lengths) if username_lengths else 0,
                "average": round(statistics.mean(username_lengths), 2) if username_lengths else 0.0,
            },
            "age_decade_distribution": dict(age_decades),
            "password_length_stats": {
                "min": min(password_lengths) if password_lengths else 0,
                "max": max(password_lengths) if password_lengths else 0,
                "average": round(statistics.mean(password_lengths), 2) if password_lengths else 0.0,
                "distribution": dict(Counter(password_lengths)),
                "short_percentage": round(
                    sum(1 for l in password_lengths if l < 8) / len(password_lengths) * 100, 2
                ) if password_lengths else 0.0,
            },
            "registration_by_year": dict(sorted(reg_years.items())),
            "timezone_distribution": dict(timezones.most_common(10))
        }

        return stats

    # -------------------------------
    # GETTER
    # -------------------------------
    def get_users(self) -> list:
        """Return validated user list."""
        return self.users