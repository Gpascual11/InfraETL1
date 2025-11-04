# new file: run_transform_load.py
import sys
import os  # <-- Import os
from pathlib import Path
from transformer import Transformer
from loader import Loader


def main():
    if len(sys.argv) != 2:
        print("Usage: python run_transform_load.py <path_to_run_directory>")
        sys.exit(1)

    run_dir = Path(sys.argv[1])
    # --- (MODIFIED) No longer need key_path ---
    # key_path = run_dir / "encryption_key.key"
    csv_path = run_dir / "valid_users.csv.enc"

    # We only check for the CSV now
    if not csv_path.exists():
        print(f"Error: Encrypted CSV not found in {run_dir}")
        print(f"Looked for: {csv_path.resolve()}")
        sys.exit(1)

    # --- (MODIFIED) Get key from environment ---
    key_str = os.environ.get("ETL_ENCRYPTION_KEY")
    if not key_str:
        print("Error: ETL_ENCRYPTION_KEY environment variable not set.")
        print("Please log in to the VM and set the variable.")
        sys.exit(1)

    # Convert key from string back to bytes
    key = key_str.encode()
    print("Encryption key loaded securely from environment.")
    # --- End of modification ---

    print("--- Running Transform ---")
    transformer = Transformer(users_input=csv_path, encryption_key=key)
    transformer.validate_data()
    stats = transformer.generate_stats()
    users_processed = transformer.get_users()

    print("--- Running Load ---")
    loader = Loader(source=users_processed, output_dir=run_dir)
    loader.save_stats_and_dashboard(users_processed, stats)

    print("--- T&L Complete ---")


if __name__ == "__main__":
    main()