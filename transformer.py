# ===============================
# CLASS 2: TRANSFORMER
# ===============================

import statistics
import re
from collections import Counter, defaultdict
from CSVHelper import CSVHelper
from validator import Validator
from pathlib import Path


class Transformer:
    """
    Transformer class:
      - Reads users from a CSV or a list of dictionaries
      - Validates and cleans user data
      - Generates descriptive statistics
      - Computes additional derived metrics (password strength, complexity, patterns)
    """

    def __init__(self, users_input):
        if isinstance(users_input, (str, Path)):
            self.users = CSVHelper.load_csv(users_input)
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
        """Generate descriptive statistics and derived metrics for cleaned dataset."""
        print("Generating statistics...")

        ages = [int(user["dob"]["age"]) for user in self.users if "dob" in user and "age" in user["dob"]]
        genders = [user["gender"] for user in self.users if "gender" in user]
        countries = [user["location"]["country"] for user in self.users if "location" in user]
        nationalities = [user["nat"] for user in self.users if "nat" in user]
        email_domains = [user["email"].split("@")[-1] for user in self.users if "email" in user]
        username_lengths = [len(user.get("login", {}).get("username", "")) for user in self.users]
        passwords = [user.get("login", {}).get("password", "") for user in self.users]

        # Age by decade
        age_decades = defaultdict(int)
        for age in ages:
            decade = (age // 10) * 10
            age_decades[f"{decade}s"] += 1

        # Password metrics
        password_lengths = [len(p) for p in passwords if p]
        password_stats = self.calculate_password_strength_stats()
        password_complexity_stats = self.calculate_password_complexity(passwords)
        password_pattern_stats = self.calculate_password_pattern_stats(passwords)

        # Correlation stats
        name_in_pass_stats = self.calculate_name_in_password(self.users)
        birthyear_in_pass_stats = self.calculate_birthyear_in_password(self.users)

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
            "password_complexity_stats": password_complexity_stats,
            "password_pattern_stats": password_pattern_stats,
            "password_strength": password_stats,
            "name_in_password": name_in_pass_stats,
            "birthyear_in_password": birthyear_in_pass_stats

        }

        return stats

    # -------------------------------
    # PASSWORD STRENGTH
    # -------------------------------
    def calculate_password_strength_stats(self):
        """Compute strong vs weak passwords metrics."""
        total = len(self.users)
        if total == 0:
            return {"strong": 0, "weak": 0, "percent_strong": 0.0, "total_users": 0}

        strong = sum(1 for user in self.users if len(user.get("login", {}).get("password", "")) > 7)
        percent_strong = round((strong / total) * 100, 2) if total else 0.0

        return {"strong": strong, "weak": total - strong, "percent_strong": percent_strong, "total_users": total}

    # -------------------------------
    # PASSWORD COMPLEXITY
    # -------------------------------
    @staticmethod
    def calculate_password_complexity(passwords):
        """Classify passwords: lowercase only, numbers only, letters+numbers, includes symbols."""
        counts = defaultdict(int)
        for p in passwords:
            if not p:
                continue
            if re.fullmatch(r"[a-z]+", p):
                counts["lowercase_only"] += 1
            elif re.fullmatch(r"\d+", p):
                counts["numbers_only"] += 1
            elif re.search(r"[^\w]", p):
                counts["includes_symbols"] += 1
            else:
                counts["letters_and_numbers"] += 1

        total = len(passwords)
        for k in counts:
            counts[k] = round(counts[k] / total * 100, 2) if total else 0.0

        return dict(counts)

    # -------------------------------
    # PASSWORD PATTERN
    # -------------------------------
    @staticmethod
    def calculate_password_pattern_stats(passwords, top_n=10):
        """Return top N most common passwords."""
        counter = Counter(passwords)
        most_common = counter.most_common(top_n)
        return [{"password": p, "count": c} for p, c in most_common]

    @staticmethod
    def calculate_name_in_password(users):
        """Return the count of users using their first or last name in password."""
        count = 0
        total = len(users)
        for user in users:
            password = user.get("login", {}).get("password", "").lower()
            first = user.get("name", {}).get("first", "").lower()
            last = user.get("name", {}).get("last", "").lower()
            if first and first in password:
                count += 1
            elif last and last in password:
                count += 1
        return {"count": count, "total": total}

    @staticmethod
    def calculate_birthyear_in_password(users):
        """Return the count of users using their birth year in password."""
        count = 0
        total = len(users)
        for user in users:
            password = user.get("login", {}).get("password", "")
            dob_date = user.get("dob", {}).get("date", "")  # ejemplo: "1952-06-18T..."
            birth_year = dob_date[:4] if dob_date else ""
            if birth_year and birth_year in password:
                count += 1
        return {"count": count, "total": total}
    # -------------------------------
    # GETTER
    # -------------------------------
    def get_users(self) -> list:
        """Return validated user list."""
        return self.users
