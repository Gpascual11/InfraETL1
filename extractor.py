# ===============================
# CLASS 1: EXTRACTOR
# ===============================

import requests

class Extractor:
    """Class responsible for extracting user data from a public API"""

    def __init__(self, api_url: str, n_users: int):
        self.api_url = api_url
        self.n_users = n_users

    def extract(self) -> list:
        print(" Downloading user data...")
        response = requests.get(f"{self.api_url}?results={self.n_users}")
        if response.status_code != 200:
            raise Exception(f"Error obtaining data: {response.status_code}")
        data = response.json()
        print(f" Downloaded {len(data['results'])} users.")
        return data["results"]