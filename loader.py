import json
import csv
import webbrowser
from pathlib import Path

class Loader:
    """Class responsible for saving transformed data and statistics to files"""

    def __init__(self, output_dir: str = "output", template_path: str = "templates/dashboard_template.html"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.template_path = Path(template_path)

    def _flatten_dict(self, d, parent_key="", sep="."):
        """Recursively flatten a nested dictionary preserving key order"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def save_to_files(self, users: list, stats: dict):
        """Save users, stats, and generate dashboard"""
        print("Saving data to files...")

        users_path = self.output_dir / "users.csv"
        stats_path = self.output_dir / "statistics.json"
        dashboard_path = self.output_dir / "dashboard.html"

        if not users:
            print("No users to save.")
            return

        # Flatten users for CSV export
        flattened_users = [self._flatten_dict(user) for user in users]
        fieldnames = list(flattened_users[0].keys())
        for user in flattened_users[1:]:
            for key in user.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        # Save users to CSV
        with open(users_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for user in flattened_users:
                writer.writerow(user)

        # Save stats to JSON
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

        # Generate dashboard HTML
        if self.template_path.exists():
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = f.read()

            # Get password stats
            password_stats = stats.get("password_strength", {})
            strong = password_stats.get("strong", 0)
            weak = password_stats.get("weak", 0)
            total = password_stats.get("total_users", 0)
            strong_percent = password_stats.get("percent_strong", 0)
            weak_percent = round(100 - strong_percent, 2)

            # Replace placeholders in the template
            html = (
                template
                .replace("{{strong}}", str(strong))
                .replace("{{weak}}", str(weak))
                .replace("{{total}}", str(total))
                .replace("{{strong_percent}}", str(strong_percent))
                .replace("{{weak_percent}}", str(weak_percent))
            )

            # Write the rendered dashboard
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(html)

            # Open dashboard in browser
            webbrowser.open_new_tab(dashboard_path.resolve().as_uri())
            print("Dashboard generated and opened in browser.")
        else:
            print("⚠️ Dashboard template not found — skipping HTML generation.")

