from extractor import Extractor
from transformer import Transformer
from loader import Loader
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet


class ETLPipeline:
    """Coordinates the ETL process: Extract, Transform, Load"""

    def __init__(self, api_url: str, n_users: int, base_output_dir: str = "output", max_workers: int = 10):
        self.api_url = api_url
        self.n_users = n_users
        self.max_workers = max_workers
        self.base_output_dir = Path(base_output_dir)
        self.timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
        self.run_dir = self.base_output_dir / self.timestamp
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # --- MODIFIED ---
        self.encryption_key = Fernet.generate_key()

        # Save the key to the run directory
        key_path = self.run_dir / "encryption_key.key"
        with open(key_path, "wb") as key_file:
            key_file.write(self.encryption_key)
        print(f"🔑 Encryption key saved to: {key_path}")
        # --- END MODIFICATION ---

    def run(self):
        print("=================================")
        print("        ETL SYSTEM START         ")
        print("=================================")
        print(f"Extracting {self.n_users} users from API...")
        print("---------------------------------")

        # ========== EXTRACT ==========
        extractor = Extractor(
            self.api_url,
            self.n_users,
            output_dir=self.run_dir,
            max_workers=self.max_workers,
            encryption_key=self.encryption_key
        )

        encrypted_csv_path = extractor.extract()

        # ========== TRANSFORM ==========
        transformer = Transformer(
            users_input=encrypted_csv_path,
            encryption_key=self.encryption_key
        )

        transformer.validate_data()
        stats = transformer.generate_stats()
        users_processed = transformer.get_users()

        # ========== LOAD ==========
        loader = Loader(source=users_processed, output_dir=self.run_dir)
        loader.save_stats_and_dashboard(users_processed, stats)

        # ========== SUMMARY ==========
        print("\n=================================")
        print("     ETL PROCESS COMPLETED       ")
        print("=================================")
        print(f"Total valid users saved: {len(users_processed)}")
        print(f"Output folder: {self.run_dir.resolve()}")
        print("Dashboard has been automatically opened in your browser.\n")