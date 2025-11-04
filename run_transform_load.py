import sys
import os
from pathlib import Path
from transformer import Transformer
from passwordauditor import PasswordAuditor
from loader import Loader

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_transform_load.py <path_to_run_directory>")
        sys.exit(1)

    run_dir = Path(sys.argv[1])
    csv_path = run_dir / "valid_users.csv.enc"

    if not csv_path.exists():
        print(f"Error: Encrypted CSV not found in {run_dir}")
        print(f"Looked for: {csv_path.resolve()}")
        sys.exit(1)

    key_str = os.environ.get("ETL_ENCRYPTION_KEY")
    if not key_str:
        print("Error: ETL_ENCRYPTION_KEY environment variable not set.")
        print("Please log in to the VM and set the variable.")
        sys.exit(1)

    key = key_str.encode()
    print("Encryption key loaded securely from environment.")

    print("--- Running Transform ---")
    transformer = Transformer(users_input=csv_path, encryption_key=key)
    transformer.validate_data()
    stats = transformer.generate_stats()
    users_processed = transformer.get_users()

    print("--- Running Password Audit ---")
    auditor = PasswordAuditor(users_processed)
    password_stats = auditor.generate_all_stats()

    stats.update(password_stats)

    print("--- Running Load ---")
    loader = Loader(source=users_processed, output_dir=run_dir)
    loader.save_stats_and_dashboard(users_processed, stats)

    print("--- T&L Complete ---")

if __name__ == "__main__":
    main()