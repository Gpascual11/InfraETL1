# ===============================
# CLASS: CSVHELPER
# ===============================

import csv
from pathlib import Path

class CSVHelper:
    """Helper class for CSV serialization/deserialization and nested dict flattening."""

    @staticmethod
    def flatten_dict(d, parent_key="", sep="."):
        """Flatten nested dictionaries for CSV writing."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(CSVHelper.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def unflatten_dict(flat_dict, sep="."):
        """Convert a flattened dict back into nested dictionary format."""
        result = {}
        for flat_key, value in flat_dict.items():
            keys = flat_key.split(sep)
            d = result
            for k in keys[:-1]:
                if k not in d:
                    d[k] = {}
                d = d[k]
            d[keys[-1]] = value
        return result

    @staticmethod
    def load_csv(csv_path):
        """
        Load users from CSV and reconstruct nested dictionaries from flattened keys.
        :param csv_path: Path to the CSV file
        :return: list of user dicts
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            print(f"⚠️ CSV file not found: {csv_path}")
            return []

        users = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user = CSVHelper.unflatten_dict(row)
                users.append(user)
        return users

    @staticmethod
    def save_to_csv(users, invalid_users, output_path=None):

        if output_path is None:
            raise ValueError("You must provide output_path, e.g., run_dir / 'valid_users.csv'")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        def write_csv(file_path, data):
            if not data:
                return
            # Flatten data
            flattened = [CSVHelper.flatten_dict(u) for u in data]
            # Collect all fieldnames
            fieldnames = []
            for u in flattened:
                for k in u.keys():
                    if k not in fieldnames:
                        fieldnames.append(k)

            # Write CSV
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened)

        # Save valid users
        write_csv(output_path, users)

        # Save invalid users if any
        if invalid_users:
            invalid_path = output_path.parent / "invalid_users.csv"
            write_csv(invalid_path, invalid_users)
            print(f"⚠️ Invalid users CSV saved at {invalid_path}")

        print(f"✅ Users CSV saved at {output_path}")


