import requests
import time
import sys
from pathlib import Path
from src.utils.validator import Validator
from src.utils.csv_helper import CSVHelper
import concurrent.futures

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

    def __init__(self, api_url: str, total_users: int = 1000, batch_size: int = 500, output_dir=None,
                 max_workers: int = 10, encryption_key: bytes = None):
        self.api_url = api_url.rstrip("?&")
        self.total_users = total_users
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.encryption_key = encryption_key
        self.all_users = []
        self.invalid_users = []
        self.validator = Validator()
        self.nationalities = self.EU_NATS + self.LATAM_NATS
        self.run_dir = Path(output_dir) if output_dir else Path("../../output")
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def _build_url(self) -> str:
        """Build API URL with nationality and results parameters."""
        nat_param = ",".join(self.nationalities)
        if "?" in self.api_url:
            return f"{self.api_url}&nat={nat_param}&results={self.batch_size}"
        else:
            return f"{self.api_url}?nat={nat_param}&results={self.batch_size}"

    def _fetch_batch(self, retry_wait: int = 5) -> tuple[list, list]:
        """Fetch a batch of users and separate valid/invalid entries (nulls only)."""
        url = self._build_url()

        try:
            response = requests.get(url, timeout=15)

            if response.status_code == 429:
                print(f"\nRate limit reached (429). Waiting {retry_wait} seconds...")
                time.sleep(retry_wait)
                return self._fetch_batch(retry_wait=min(retry_wait * 2, 60))

            if response.status_code != 200:
                raise Exception(f"Error obtaining data: {response.status_code}")

            data = response.json()
            if "results" not in data:
                raise Exception("missing 'results' key.")

            users = data["results"]

            valid = []
            invalid = []
            for user in users:
                if self.validator.is_valid_value(user):
                    valid.append(user)
                else:
                    invalid.append(user)

            return valid, invalid

        except requests.RequestException as e:
            print(f"\nNetwork error: {e}")
            time.sleep(5)
            return [], []

    def extract(self) -> Path:
        """
        Starts the multi-threaded extraction process, collects users, and saves them to an encrypted CSV.
        :return: Path to the saved valid users CSV file.
        """
        print(f"\nStarting extraction of {self.total_users} users...\n")

        estimated_valid_per_batch = int(self.batch_size * 0.85)
        if estimated_valid_per_batch == 0:
            estimated_valid_per_batch = 1

        estimated_batches_needed = (self.total_users + estimated_valid_per_batch - 1) // estimated_valid_per_batch

        initial_workers_to_launch = min(estimated_batches_needed, self.max_workers)

        print(
            f"Estimated batches: {estimated_batches_needed}. Launching {initial_workers_to_launch} initial worker(s)...")

        futures = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for _ in range(initial_workers_to_launch):
                futures.add(executor.submit(self._fetch_batch))

            while futures:
                done_iter = concurrent.futures.as_completed(futures)
                try:
                    future = next(done_iter)
                except StopIteration:
                    break

                try:
                    valid, invalid = future.result()
                    self.all_users.extend(valid)
                    self.invalid_users.extend(invalid)
                except Exception as e:
                    print(f"\nError processing a batch: {e}")

                futures.remove(future)

                current_count = min(len(self.all_users), self.total_users)
                _print_progress(current_count, self.total_users)

                if len(self.all_users) < self.total_users:
                    futures.add(executor.submit(self._fetch_batch))

        if len(self.all_users) > self.total_users:
            self.all_users = self.all_users[: self.total_users]

        print("\n\nExtraction completed.")
        print(f"Valid users: {len(self.all_users)}")
        print(f"Invalid users: {len(self.invalid_users)}")

        csv_output_path = self.run_dir / "valid_users.csv.enc"

        CSVHelper.save_to_csv(
            self.all_users,
            self.invalid_users,
            output_path=csv_output_path,
            key=self.encryption_key
        )

        return csv_output_path