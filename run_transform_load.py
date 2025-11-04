# new file: run_transform_load.py
import sys
from pathlib import Path
from transformer import Transformer
from loader import Loader

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_transform_load.py <path_to_run_directory>")
        sys.exit(1)

    run_dir = Path(sys.argv[1])
    key_path = run_dir / "encryption_key.key"
    csv_path = run_dir / "valid_users.csv.enc"

    if not key_path.exists() or not csv_path.exists():
        print(f"Error: Files not found in {run_dir}")
        sys.exit(1)

    # Read the key
    with open(key_path, "rb") as f:
        key = f.read()

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