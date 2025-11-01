# ===============================
# CLASS 1: EXTRACTOR
# ===============================

import requests
import time
import sys


class Extractor:
    """Class responsible for extracting and validating user data from the RandomUser API"""

    # Define nationality codes (EU + LATAM)
    EU_NATS = ["CH", "DE", "DK", "ES", "FI", "FR", "GB", "IE", "NL", "NO", "TR", "RS", "UA"]
    LATAM_NATS = ["BR", "MX"]

    def __init__(self, api_url: str, total_users: int = 1000, batch_size: int = 500):
        """
        :param api_url: Base API URL (e.g. "https://randomuser.me/api/")
        :param total_users: Total number of users to collect
        :param batch_size: Number of users per API request
        """
        self.api_url = api_url.rstrip("?&")
        self.total_users = total_users
        self.batch_size = batch_size
        self.all_users = []

        # Combine EU and LATAM nationalities
        self.nationalities = self.EU_NATS + self.LATAM_NATS

    # -------------------------------
    # INTERNAL METHODS
    # -------------------------------

    def _build_url(self) -> str:
        """Build API URL with desired nationalities and batch size"""
        nat_param = ",".join(self.nationalities)
        if "?" in self.api_url:
            return f"{self.api_url}&nat={nat_param}&results={self.batch_size}"
        else:
            return f"{self.api_url}?nat={nat_param}&results={self.batch_size}"

    def _fetch_batch(self) -> list:
        """Fetch one batch of users, retry if rate-limited"""
        url = self._build_url()
        print(f"Requesting {self.batch_size} users from {url}")

        try:
            response = requests.get(url)
            if response.status_code == 429:
                print("Rate limit reached (429). Waiting 10 seconds before retrying...")
                time.sleep(10)
                return self._fetch_batch()  # Retry recursively

            if response.status_code != 200:
                raise Exception(f"Error obtaining data: {response.status_code}")

            data = response.json()
            if "results" not in data:
                raise Exception("Unexpected API response: missing 'results' key.")

            users = data["results"]
            valid_users = self._filter_invalid(users)
            return valid_users

        except requests.RequestException as e:
            print(f"Network error: {e}")
            time.sleep(5)
            return []

    def _is_valid_value(self, value) -> bool:
        """Recursively check if all fields in a structure are non-null and non-empty"""
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, dict):
            return all(self._is_valid_value(v) for v in value.values())
        if isinstance(value, list):
            return all(self._is_valid_value(v) for v in value)
        return True

    def _filter_invalid(self, users: list) -> list:
        """Remove any users that contain null or empty fields anywhere"""
        valid_users = []
        removed_count = 0

        for user in users:
            try:
                if self._is_valid_value(user):
                    valid_users.append(user)
                else:
                    removed_count += 1
            except Exception:
                removed_count += 1
                continue

        if removed_count > 0:
            print(f"Removed {removed_count} invalid or incomplete records.")
        return valid_users

    def _print_progress(self, current: int, total: int, bar_length: int = 40):
        """Display a simple progress bar in console"""
        progress = current / total
        filled = int(bar_length * progress)
        bar = "#" * filled + "-" * (bar_length - filled)
        percent = progress * 100
        sys.stdout.write(f"\rProgress: [{bar}] {percent:.1f}% ({current}/{total})")
        sys.stdout.flush()

    # -------------------------------
    # PUBLIC METHOD
    # -------------------------------

    def extract(self) -> list:
        """Extract all users until total_users is reached"""
        print(f"\nStarting extraction of {self.total_users} EU/LATAM users...\n")

        while len(self.all_users) < self.total_users:
            batch = self._fetch_batch()
            self.all_users.extend(batch)

            # Ensure we don't exceed the target number
            if len(self.all_users) > self.total_users:
                self.all_users = self.all_users[: self.total_users]

            # Update progress bar
            self._print_progress(len(self.all_users), self.total_users)
            time.sleep(1)

        print("\nExtraction completed successfully.\n")
        return self.all_users
