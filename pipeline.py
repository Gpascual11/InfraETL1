from extractor import Extractor
from transformer import Transformer
from loader import Loader
from datetime import datetime
from pathlib import Path


class ETLPipeline:
    """Coordinates the ETL process: Extract, Transform, Load"""

    def __init__(self, api_url: str, n_users: int, base_output_dir: str = "output"):
        self.api_url = api_url
        self.n_users = n_users
        self.base_output_dir = Path(base_output_dir)
        self.timestamp = datetime.now().strftime("%Y_%m_%d|%H:%M:%S:")
        self.run_dir = self.base_output_dir / self.timestamp
        self.run_dir.mkdir(parents=True, exist_ok=True)


    def run(self):
        print("=================================")
        print("        ETL SYSTEM START         ")
        print("=================================")
        print(f"Extracting {self.n_users} users from API...")
        print("---------------------------------")


        # ========== EXTRACT ==========
        extractor = Extractor(self.api_url, self.n_users, output_dir=self.run_dir)
        users = extractor.extract()

        # ========== TRANSFORM ==========
        transformer = Transformer(users)
        transformer.validate_data()
        stats = transformer.generate_stats()
        users_processed = transformer.get_users()

        # Add password strength stats
        password_stats = transformer.calculate_password_strength_stats()
        stats["password_strength"] = password_stats

        # ========== LOAD ==========
        loader = Loader(source=users_processed, output_dir=self.run_dir)
        loader.save_stats_and_dashboard(users_processed, stats)

        # ========== SUMMARY ==========
        print("\n=================================")
        print("     ETL PROCESS COMPLETED ✅     ")
        print("=================================")
        print(f"Total valid users saved: {len(users_processed)}")
        print(f"Output folder: {self.run_dir.resolve()}")
        print("Dashboard has been automatically opened in your browser.\n")
