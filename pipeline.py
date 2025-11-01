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
        print("Starting ETL process...\n")

        # EXTRACT
        extractor = Extractor(self.api_url, self.n_users)
        users = extractor.extract()

        # TRANSFORM
        transformer = Transformer(users)
        stats = transformer.generate_stats()
        users_processed = transformer.get_users()

        # LOAD
        loader = Loader(self.output_dir)
        loader.save_to_files(users_processed, stats)

        print("\nProcess finished successfully.")
        print("Summary:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
