# ===============================
# CLASS 1: EXTRACTOR
# ===============================

import requests   # Library for HTTP requests
import time       # Used to wait between requests (avoid rate-limiting)
import sys        # For console output (progress bar)
from validator import Validator  # Import shared validation logic


def _print_progress(current: int, total: int, bar_length: int = 40):
    """
    Display a progress bar in the console to visualize extraction progress.

    Example:
    Progress: [##########----------] 50.0% (500/1000)
    """
    progress = current / total
    filled = int(bar_length * progress)
    bar = "#" * filled + "-" * (bar_length - filled)
    percent = progress * 100
    sys.stdout.write(f"\rProgress: [{bar}] {percent:.1f}% ({current}/{total})")
    sys.stdout.flush()


class Extractor:
    """
    Class responsible for extracting user data from the RandomUser API
    and validating it using the Validator class.
    """

    # Nationality codes for European and Latin American countries
    EU_NATS = ["CH", "DE", "DK", "ES", "FI", "FR", "GB", "IE", "NL", "NO", "TR", "RS", "UA"]
    LATAM_NATS = ["BR", "MX"]

    def __init__(self, api_url: str, total_users: int = 1000, batch_size: int = 500):
        """
        Initialize the Extractor instance.

        :param api_url: Base API endpoint (e.g., "https://randomuser.me/api/")
        :param total_users: Total number of users to collect
        :param batch_size: Number of users per request
        """
        self.api_url = api_url.rstrip("?&")    # Remove trailing ? or & for safety
        self.total_users = total_users          # Target number of users to collect
        self.batch_size = batch_size            # Users fetched per API call
        self.all_users = []                     # Container for all validated users
        self.validator = Validator()            # Shared validator instance

        # Combine all nationalities to request
        self.nationalities = self.EU_NATS + self.LATAM_NATS

    # -------------------------------
    # INTERNAL METHODS
    # -------------------------------

    def _build_url(self) -> str:
        """
        Construct the full API URL including nationality and result parameters.

        Example:
        https://randomuser.me/api/?nat=es,fr,de&results=500
        """
        nat_param = ",".join(self.nationalities)

        # Append parameters correctly depending on whether "?" already exists
        if "?" in self.api_url:
            return f"{self.api_url}&nat={nat_param}&results={self.batch_size}"
        else:
            return f"{self.api_url}?nat={nat_param}&results={self.batch_size}"

    def _fetch_batch(self) -> list:
        """
        Request one batch of users from the API and validate the data.
        Handles rate-limiting and connection errors gracefully.
        """
        url = self._build_url()
        print(f"Requesting {self.batch_size} users from {url}")

        try:
            # Perform the HTTP GET request
            response = requests.get(url)

            # Handle HTTP 429 (Too Many Requests)
            if response.status_code == 429:
                print("Rate limit reached (429). Waiting 10 seconds before retrying...")
                time.sleep(10)
                return self._fetch_batch()  # Retry recursively

            # Raise an error for any other non-OK status code
            if response.status_code != 200:
                raise Exception(f"Error obtaining data: {response.status_code}")

            # Parse JSON response
            data = response.json()
            if "results" not in data:
                raise Exception("Unexpected API response: missing 'results' key.")

            # Extract user list
            users = data["results"]

            # Validate users using the Validator class
            valid_users = self.validator.validate_batch(users)
            return valid_users

        except requests.RequestException as e:
            # Handle connection issues
            print(f"Network error: {e}")
            time.sleep(5)
            return []

    # -------------------------------
    # PUBLIC METHOD
    # -------------------------------

    def extract(self) -> list:
        """
        Execute the full extraction process:
        - Continuously request user batches until the total target is reached.
        - Validate and clean each batch using Validator.
        - Show extraction progress on the console.
        - Return a final list of validated users.
        """
        print(f"\nStarting extraction of {self.total_users} EU/LATAM users...\n")

        while len(self.all_users) < self.total_users:
            # Fetch and validate a batch
            batch = self._fetch_batch()
            self.all_users.extend(batch)

            # Trim extra users if we exceed the target
            if len(self.all_users) > self.total_users:
                self.all_users = self.all_users[: self.total_users]

            # Update progress bar
            _print_progress(len(self.all_users), self.total_users)
            time.sleep(1)

        print("\nExtraction completed successfully.\n")
        return self.all_users
