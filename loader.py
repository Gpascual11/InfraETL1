import json
import csv
from pathlib import Path

class Loader:
    """Class responsible for saving transformed data and statistics to files"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def _flatten_dict(self, d, parent_key="", sep="."):
        """Recursively flatten a nested dictionary preserving key order"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def save_to_files(self, users: list, stats: dict):
        """Save users and statistics to CSV and JSON files, preserving field order."""
        print("Saving data to files...")

        users_path = self.output_dir / "users.csv"
        stats_path = self.output_dir / "statistics.json"

        if not users:
            print("No users to save.")
            return

        # Flatten users, preserving field order
        flattened_users = [self._flatten_dict(user) for user in users]

        # Build ordered list of fieldnames based on first user
        fieldnames = list(flattened_users[0].keys())

        # Add any new fields from later users (preserving overall order)
        for user in flattened_users[1:]:
            for key in user.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        # Write to CSV
        with open(users_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for user in flattened_users:
                writer.writerow(user)

        # Save statistics as JSON
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

        print(f"Data saved in: {self.output_dir.resolve()}")