# ===============================
# CLASS 2: TRANSFORMER
# ===============================

import statistics
from collections import Counter

class Transformer:
    """Class responsible for transforming user data and generating statistics"""

    def __init__(self, users: list):
        self.users = users

    def generate_stats(self) -> dict:
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
        """Return the processed user list (ready to save)."""
        return self.users
