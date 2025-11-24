import sys
import argparse
import os
from datetime import datetime
from pathlib import Path

# Truco para calcular la ruta correcta sin importar en qué VM estés
# 1. Obtenemos donde está este script (InfraETL1/scripts)
CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
# 2. Subimos un nivel para ir a la raíz del proyecto (InfraETL1)
PROJECT_ROOT = CURRENT_SCRIPT_DIR.parent

# AÑADIMOS EL PROYECTO AL PATH DE PYTHON para que encuentre 'src'
sys.path.append(str(PROJECT_ROOT))

# Ahora sí podemos importar
from src.etl.extractor import Extractor


def main(n_users: int, max_workers: int):
    api_url = "https://randomuser.me/api/"

    base_output_dir = PROJECT_ROOT / "output"

    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    run_dir = base_output_dir / timestamp

    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Running Extraction ---")
    print(f"Output directory: {run_dir.resolve()}")

    key_str = os.environ.get("ETL_ENCRYPTION_KEY")
    if not key_str:
        print("Error: Environment variable ETL_ENCRYPTION_KEY not set.")
        sys.exit(1)

    encryption_key = key_str.encode()
    print("Encryption key loaded securely from environment.")

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