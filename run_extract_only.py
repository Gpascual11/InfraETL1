# new file: run_extract_only.py
import sys
import argparse
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

    # Generate and save the encryption key
    encryption_key = Fernet.generate_key()
    key_path = run_dir / "encryption_key.key"
    with open(key_path, "wb") as key_file:
        key_file.write(encryption_key)
    print(f"Encryption key saved to: {key_path}")

    # ========== EXTRACT ==========
    extractor = Extractor(
        api_url,
        n_users,
        output_dir=run_dir,
        max_workers=max_workers,
        encryption_key=encryption_key
    )

    # This saves valid_users.csv.enc and invalid_users.csv.enc
    extractor.extract()
    print("--- Extraction Complete ---")


if __name__ == "__main__":
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