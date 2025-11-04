# new file: run_extract_only.py
import sys
import argparse
import os  # <-- Import os
from extractor import Extractor
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet


def main(n_users: int, max_workers: int):
    api_url = "https://randomuser.me/api/"
    base_output_dir = Path("output")
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    run_dir = base_output_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Running Extraction ---")
    print(f"Output directory: {run_dir.resolve()}")

    # --- (MODIFIED) Get key from environment ---
    key_str = os.environ.get("ETL_ENCRYPTION_KEY")
    if not key_str:
        print("Error: ETL_ENCRYPTION_KEY environment variable not set.")
        print("Please log in to the VM and set the variable.")
        sys.exit(1)

    # Convert key from string back to bytes
    encryption_key = key_str.encode()
    print("Encryption key loaded securely from environment.")
    # --- End of modification ---

    # We no longer save the key file

    # ========== EXTRACT ==========
    extractor = Extractor(
        api_url,
        n_users,
        output_dir=run_dir,
        max_workers=max_workers,
        encryption_key=encryption_key
    )

    extractor.extract()
    print("--- Extraction Complete ---")


if __name__ == "__main__":
    # ... (The __main__ block is unchanged) ...
    parser = argparse.ArgumentParser(description="Run ETL Extraction Step")
    parser.add_argument(
        "users",
        type=int,
        help="Number of users to extract"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Max concurrent workers"
    )

    args = parser.parse_args()

    if args.users <= 0:
        print("Error: Number of users must be greater than 0.")
        sys.exit(1)

    main(n_users=args.users, max_workers=args.workers)