# ===============================
# CLASS 3: LOADER
# ===============================

import json
from pathlib import Path
import pandas as pd

class Loader:
    """Class responsible for saving transformed data and statistics to files"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_to_files(self, df: pd.DataFrame, stats: dict):
        """Guarda los datos en ficheros CSV y JSON"""
        print("Saving data to files...")

        users_path = self.output_dir / "users.csv"
        stats_path = self.output_dir / "statistics.json"

        df.to_csv(users_path, index=False)
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

        print(f"Data saved in: {self.output_dir.resolve()}")