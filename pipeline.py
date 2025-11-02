# ===============================
# CLASS 4: PIPELINE ETL
# ===============================

from extractor import Extractor
from transformer import Transformer
from loader import Loader


class ETLPipeline:
    """Coordinates the ETL process: Extract, Transform, Load"""

    def __init__(self, api_url: str, n_users: int, output_dir: str = "output"):
        self.api_url = api_url
        self.n_users = n_users
        self.output_dir = output_dir

    def run(self):
        print("=================================")
        print("        ETL SYSTEM START         ")
        print("=================================")
        print(f"Extracting {self.n_users} users from API...")
        print("---------------------------------")

        # ========== EXTRACT ==========
        extractor = Extractor(self.api_url, self.n_users)
        users = extractor.extract()

        # ========== TRANSFORM ==========
        transformer = Transformer(users)
        transformer.validate_data()  # detect anomalies etc.
        stats = transformer.generate_stats()
        users_processed = transformer.get_users()

        # Add password strength stats
        password_stats = transformer.calculate_password_strength_stats()
        stats["password_strength"] = password_stats

        # ========== LOAD ==========
        loader = Loader(self.output_dir)
        loader.save_to_files(users_processed, stats)

        # ========== SUMMARY ==========
        print("\n=================================")
        print("     ETL PROCESS COMPLETED ✅     ")
        print("=================================")
        print(f"Total valid users saved: {len(users_processed)}")
        print(f"Output files stored in '{self.output_dir}' folder.")
        print("Dashboard has been automatically opened in your browser.\n")
