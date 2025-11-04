# ===============================
# CLASS: PASSWORD AUDITOR
# ===============================

import re
import math
import string
from collections import Counter, defaultdict


class PasswordAuditor:
    """
    Performs security-focused analysis on user passwords.
    - Calculates strength, complexity, and common patterns.
    - Checks for correlations (name/birthyear in password).
    """

    def __init__(self, users: list):
        self.users = users
        self.passwords = [user.get("login", {}).get("password", "") for user in self.users]

    def generate_all_stats(self) -> dict:
        """Runs all password audit methods and returns a combined dictionary."""

        password_complexity_stats = self.calculate_password_complexity()
        password_pattern_stats = self.calculate_password_pattern_stats()
        password_strength_stats = self.calculate_password_strength_stats()
        name_in_pass_stats = self.calculate_name_in_password()
        birthyear_in_pass_stats = self.calculate_birthyear_in_password()
        username_in_pass_stats = self.calculate_username_in_password()

        # Combine all stats into a single dictionary
        all_stats = {
            "password_complexity_stats": password_complexity_stats,
            "password_pattern_stats": password_pattern_stats,
            "password_strength": password_strength_stats,
            "name_in_password": name_in_pass_stats,
            "birthyear_in_password": birthyear_in_pass_stats,
            "username_in_password": username_in_pass_stats,
        }
        return all_stats

    # -------------------------------
    # PASSWORD STRENGTH
    # -------------------------------
    def calculate_password_strength_stats(self, entropy_threshold=50):
        """
        Compute strong vs weak passwords metrics using entropy and complexity rules.
        """
        total = len(self.users)
        if total == 0:
            return {"strong": 0, "weak": 0, "percent_strong": 0.0, "total_users": 0}

        def estimate_entropy(password):
            """Estimate entropy based on character set size R and length L."""
            if not password:
                return 0.0

            R = 0
            if any(c.islower() for c in password): R += 26
            if any(c.isupper() for c in password): R += 26
            if any(c.isdigit() for c in password): R += 10
            if any(c in string.punctuation for c in password): R += len(string.punctuation)
            if any(c.isspace() for c in password): R += 1

            L = len(password)
            return L * math.log2(R) if R > 0 else 0.0

        def check_complexity(password):
            """
            Checks if password meets basic complexity rules.
            Requires at least 3 of 4 types: lower, upper, digit, symbol.
            """
            if not password:
                return False

            types = 0
            if any(c.islower() for c in password): types += 1
            if any(c.isupper() for c in password): types += 1
            if any(c.isdigit() for c in password): types += 1
            if any(c in string.punctuation for c in password): types += 1

            return types >= 3

        strong = 0
        for user in self.users:
            password = user.get("login", {}).get("password", "")

            passes_entropy = estimate_entropy(password) >= entropy_threshold
            passes_complexity = check_complexity(password)

            if passes_entropy and passes_complexity:
                strong += 1

        percent_strong = round((strong / total) * 100, 2)

        return {
            "strong": strong,
            "weak": total - strong,
            "percent_strong": percent_strong,
            "total_users": total
        }

    # -------------------------------
    # PASSWORD COMPLEXITY
    # -------------------------------
    def calculate_password_complexity(self):
        """Classify passwords: lowercase only, numbers only, letters+numbers, includes symbols."""
        counts = defaultdict(int)
        for p in self.passwords:
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
        return dict(counts)

    # -------------------------------
    # PASSWORD PATTERN
    # -------------------------------
    def calculate_password_pattern_stats(self, top_n=10):
        """Return top N most common passwords."""
        counter = Counter(self.passwords)
        most_common = counter.most_common(top_n)
        return [{"password": p, "count": c} for p, c in most_common]

    def calculate_name_in_password(self):
        """Return the count of users using their first or last name in password."""
        count = 0
        total = len(self.users)
        for user in self.users:
            password = user.get("login", {}).get("password", "").lower()
            first = user.get("name", {}).get("first", "").lower()
            last = user.get("name", {}).get("last", "").lower()
            if (first and first in password) or (last and last in password):
                count += 1
        return {"count": count, "total": total}

    def calculate_birthyear_in_password(self):
        """Return the count of users using their birth year in password."""
        count = 0
        total = len(self.users)
        for user in self.users:
            password = user.get("login", {}).get("password", "")
            dob_date = user.get("dob", {}).get("date", "")
            birth_year = dob_date[:4] if dob_date else ""
            if birth_year and birth_year in password:
                count += 1
        return {"count": count, "total": total}

    def calculate_username_in_password(self):
        """Return the count of users using their username in password."""
        count = 0
        total = len(self.users)
        for user in self.users:
            password = user.get("login", {}).get("password", "").lower()
            username = user.get("login", {}).get("username", "").lower()
            if username and username in password:
                count += 1
        return {"count": count, "total": total}