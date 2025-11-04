# ===============================
# CLASS: CSVHELPER
# ===============================

import csv
from pathlib import Path
import io
from cryptography.fernet import Fernet


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
    def load_csv(csv_path, key: bytes = None):
        """
        Load users from CSV. If a key is provided, decrypts the file first.
        :param csv_path: Path to the CSV file (can be .csv or .csv.enc)
        :param key: Fernet encryption key (optional)
        :return: list of user dicts
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            print(f"Warning: CSV file not found: {csv_path}")
            return []

        users = []

        try:
            if key:
                # --- Decryption logic ---
                fernet = Fernet(key)
                with open(csv_path, "rb") as f:
                    encrypted_data = f.read()

                decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')

                # Use in-memory buffer for DictReader
                buffer = io.StringIO(decrypted_data)
                reader = csv.DictReader(buffer)
                for row in reader:
                    user = CSVHelper.unflatten_dict(row)
                    users.append(user)

            else:
                # --- Original plaintext logic ---
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        user = CSVHelper.unflatten_dict(row)
                        users.append(user)

        except Exception as e:
            print(f"Error loading CSV {csv_path}: {e}")
            if key:
                print("This may be due to an incorrect encryption key or corrupted file.")
            return []

        return users

    @staticmethod
    def save_to_csv(users, invalid_users, output_path=None, key: bytes = None):

        if output_path is None:
            raise ValueError("You must provide output_path, e.g., run_dir / 'valid_users.csv'")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        def write_csv(file_path, data, encryption_key):
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

            # Write to an in-memory buffer first
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened)

            csv_data_str = buffer.getvalue()
            buffer.close()

            if encryption_key:
                # --- Encryption logic ---
                fernet = Fernet(encryption_key)
                encrypted_data = fernet.encrypt(csv_data_str.encode('utf-8'))
                with open(file_path, "wb") as f:
                    f.write(encrypted_data)
            else:
                # --- Original plaintext logic ---
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    f.write(csv_data_str)

        # Save valid users
        write_csv(output_path, users, key)
        print(f"Users CSV saved at {output_path}")

        # Save invalid users if any
        if invalid_users:
            suffix = ".enc" if key else ""
            invalid_path = output_path.parent / f"invalid_users.csv{suffix}"
            write_csv(invalid_path, invalid_users, key)
            print(f"Invalid users CSV saved at {invalid_path}")