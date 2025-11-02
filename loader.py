# ===============================
# CLASS: LOADER
# ===============================

import json
import webbrowser
from pathlib import Path


class Loader:
    """Class responsible for saving transformed data and statistics to files"""

    def __init__(self, output_dir="output", template_path="templates/dashboard_template.html"):
        self.run_dir = Path(output_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)  # safe to ensure exists
        self.template_path = Path(template_path)
        self.timestamp = self.run_dir.name  # extract timestamp from folder name

    # ---------------------------
    # Save files
    # ---------------------------
    def save_to_files(self, users: list, stats: dict):
        """Save users, stats, and generate dashboard in the run folder"""
        if not users:
            print("No users to save.")
            return

        # Paths
        stats_path = self.run_dir / "statistics.json"
        dashboard_path = self.run_dir / "dashboard.html"

        # Save stats JSON
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

        # Generate dashboard HTML
        if self.template_path.exists():
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = f.read()

            # Password stats safely
            password_stats = stats.get("password_strength", {})
            strong = password_stats.get("strong", 0)
            weak = password_stats.get("weak", 0)
            total = password_stats.get("total_users", 0)
            strong_percent = password_stats.get("percent_strong", 0)
            weak_percent = round(100 - strong_percent, 2)

            # Replace placeholders
            html = (
                template.replace("{{strong}}", str(strong))
                .replace("{{weak}}", str(weak))
                .replace("{{total}}", str(total))
                .replace("{{strong_percent}}", str(strong_percent))
                .replace("{{weak_percent}}", str(weak_percent))
                .replace("{{timestamp}}", self.timestamp)
            )

            # Save and open dashboard
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open_new_tab(dashboard_path.resolve().as_uri())
            print("✅ Dashboard generated and opened in browser.")
        else:
            print("⚠️ Dashboard template not found — skipping HTML generation.")

        print(f"✅ Stats saved: {stats_path}")
