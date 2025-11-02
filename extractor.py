# ===============================
# CLASS 1: EXTRACTOR
# ===============================

import requests
import time
import sys
import csv
from pathlib import Path
from validator import Validator


def _print_progress(current: int, total: int, bar_length: int = 40):
    """Display a console progress bar."""
    progress = current / total
    filled = int(bar_length * progress)
    bar = "#" * filled + "-" * (bar_length - filled)
    percent = progress * 100
    sys.stdout.write(f"\rProgress: [{bar}] {percent:.1f}% ({current}/{total})")
    sys.stdout.flush()


class Extractor:
    """
    Extractor class:
    - Fetches users from the RandomUser API
    - Validates only null/empty fields
    - Saves valid and invalid users to CSV
    """

    EU_NATS = ["CH", "DE", "DK", "ES", "FI", "FR", "GB", "IE", "NL", "NO", "TR", "RS", "UA"]
    LATAM_NATS = ["BR", "MX"]

    def __init__(self, api_url: str, total_users: int = 1000, batch_size: int = 500, output_dir: Path = None):
        self.api_url = api_url.rstrip("?&")
        self.total_users = total_users
        self.batch_size = batch_size
        self.all_users = []
        self.invalid_users = []
        self.validator = Validator()
        self.nationalities = self.EU_NATS + self.LATAM_NATS
        self.output_dir = Path(output_dir) if output_dir else Path("output")


    # -------------------------------
    # INTERNAL METHODS
    # -------------------------------

    def _build_url(self) -> str:
        """Build API URL with parameters."""
        nat_param = ",".join(self.nationalities)
        if "?" in self.api_url:
            return f"{self.api_url}&nat={nat_param}&results={self.batch_size}"
        else:
            return f"{self.api_url}?nat={nat_param}&results={self.batch_size}"

    def _fetch_batch(self) -> tuple[list, list]:
        """Fetch a batch of users and separate valid/invalid entries (nulls only)."""
        url = self._build_url()
        print(f"\nRequesting {self.batch_size} users from {url}")

        try:
            response = requests.get(url)
            if response.status_code == 429:
                print("Rate limit reached (429). Waiting 10 seconds before retrying...")
                time.sleep(10)
                return self._fetch_batch()

            if response.status_code != 200:
                raise Exception(f"Error obtaining data: {response.status_code}")

            data = response.json()
            if "results" not in data:
                raise Exception("Unexpected API response: missing 'results' key.")

            users = data["results"]

            # Separate valid/invalid based on null/empty only
            valid = []
            invalid = []
            for user in users:
                if self.validator.is_valid_value(user):
                    valid.append(user)
                else:
                    invalid.append(user)

            return valid, invalid

        except requests.RequestException as e:
            print(f"Network error: {e}")
            time.sleep(5)
            return [], []

    def _save_to_csv(self, valid_users, invalid_users):

        valid_path = self.output_dir / "valid_users.csv"
        invalid_path = self.output_dir / "invalid_users.csv"

        def write_csv(path, users):
            if not users:
                return
            flat_users = [Validator.flatten_dict(u) for u in users]
            fieldnames = list(flat_users[0].keys())
            for u in flat_users[1:]:
                for k in u.keys():
                    if k not in fieldnames:
                        fieldnames.append(k)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flat_users)

        write_csv(valid_path, valid_users)
        write_csv(invalid_path, invalid_users)
        print(f"\n✅ Saved {len(valid_users)} valid users → {valid_path}")
        print(f"⚠️ Saved {len(invalid_users)} invalid users → {invalid_path}")

    # -------------------------------
    # PUBLIC METHOD
    # -------------------------------

    def extract(self) -> list:
        print(f"\n🚀 Starting extraction of {self.total_users} users...\n")

        while len(self.all_users) < self.total_users:
            valid, invalid = self._fetch_batch()
            self.all_users.extend(valid)
            self.invalid_users.extend(invalid)

            if len(self.all_users) > self.total_users:
                self.all_users = self.all_users[: self.total_users]

            _print_progress(len(self.all_users), self.total_users)
            time.sleep(1)

        print("\n\n✅ Extraction completed.")
        print(f"→ Valid users: {len(self.all_users)}")
        print(f"→ Invalid users: {len(self.invalid_users)}")

        self._save_to_csv(self.all_users, self.invalid_users)
        return self.all_users