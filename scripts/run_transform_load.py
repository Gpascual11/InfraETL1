import sys
import os
from pathlib import Path

CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT))

from src.etl.transformer import Transformer
from src.utils.passwordauditor import PasswordAuditor
from src.etl.loader import Loader


def main():
    if len(sys.argv) != 2:
        print("Usage: python run_transform_load.py <path_to_run_directory>")
        sys.exit(1)

    relative_run_path = sys.argv[1]

    run_dir = PROJECT_ROOT / relative_run_path

    csv_path = run_dir / "valid_users.csv.enc"

    if not csv_path.exists():
        print(f"Error: Encrypted CSV not found.")
        print(f"Looked in: {csv_path.resolve()}")
        if run_dir.exists():
            print(f"Contents of {run_dir.name}: {[p.name for p in run_dir.glob('*')]}")
        sys.exit(1)

    key_str = os.environ.get("ETL_ENCRYPTION_KEY")
    if not key_str:
        print("Environment variable ETL_ENCRYPTION_KEY not set.")
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