# ===============================
# CLASS: LOADER
# ===============================

import json
import webbrowser
from pathlib import Path
from CSVHelper import CSVHelper


class Loader:
    """Class responsible for saving transformed data and statistics to files"""


    def __init__(self, source, output_dir="output", template_path="templates/dashboard_template.html"):
        self.run_dir = Path(output_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)  # asegurarse que exista
        self.template_path = Path(template_path)
        self.timestamp = self.run_dir.name  # extrae timestamp de la carpeta
        self.users = []  # inicializar la lista
        self.load_users(source)  # ahora source está definido

    def load_users(self, source):
        # carga usuarios desde CSV o lista
        if isinstance(source, list):
            self.users = source
        else:
            self.users = CSVHelper.load_csv(source)

    # ---------------------------
    # Save files
    # ---------------------------
    def save_stats_and_dashboard(self, users: list, stats: dict):
        """Save stats and generate dashboard in the run folder with charts and tables."""
        if not users:
            print("No users to save.")
            return

        stats_path = self.run_dir / "statistics.json"
        dashboard_path = self.run_dir / "dashboard.html"

        # Save stats JSON
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

        # Load template
        if not self.template_path.exists():
            print("⚠️ Dashboard template not found — skipping HTML generation.")
            return
        template = self.template_path.read_text(encoding="utf-8")

        # Password stats
        password_stats = stats.get("password_strength", {})
        strong = password_stats.get("strong", 0)
        weak = password_stats.get("weak", 0)
        strong_percent = password_stats.get("percent_strong", 0)
        weak_percent = 100 - strong_percent
        short_password_percent = stats.get("password_length_stats", {}).get("short_percentage", 0)

        # For display
        name_in_password_stats = stats.get("name_in_password", {"count": 0, "total": 0})
        birthyear_in_password_stats = stats.get("birthyear_in_password", {"count": 0, "total": 0})
        name_in_password_display = f"{name_in_password_stats['count']} / {name_in_password_stats['total']}"
        birthyear_in_password_display = f"{birthyear_in_password_stats['count']} / {birthyear_in_password_stats['total']}"

        # For chart
        name_in_password_percent = round(
            (name_in_password_stats['count'] / name_in_password_stats['total'] * 100)
            if name_in_password_stats['total'] else 0.0, 2
        )
        birthyear_in_password_percent = round(
            (birthyear_in_password_stats['count'] / birthyear_in_password_stats['total'] * 100)
            if birthyear_in_password_stats['total'] else 0.0, 2
        )

        # Generate user table rows
        user_rows = ""
        for user in users:
            uid = user.get("login", {}).get("uuid", "")
            username = user.get("login", {}).get("username", "")
            email = user.get("email", "")
            country = user.get("location", {}).get("country", "")
            password = user.get("login", {}).get("password", "")
            strength = "Strong" if len(password) > 7 else "Weak"
            user_rows += f"<tr><td>{uid}</td><td>{username}</td><td>{email}</td><td>{country}</td><td>{strength}</td></tr>"

        country_labels = list(stats['users_per_country'].keys())
        country_counts_list = list(stats['users_per_country'].values())
        country_colors = [f"hsl({i * 35 % 360},70%,50%)" for i in range(len(country_labels))]

        gender_labels = list(stats['gender_distribution'].keys())
        gender_counts_list = list(stats['gender_distribution'].values())

        age_decade_labels = list(stats['age_decade_distribution'].keys())
        age_decade_counts = list(stats['age_decade_distribution'].values())
        age_decade_colors = [f"hsl({i * 45 % 360},70%,50%)" for i in range(len(age_decade_labels))]

        html = template.replace("{{strong}}", str(strong)) \
            .replace("{{weak}}", str(weak)) \
            .replace("{{total}}", str(stats.get("total_users", 0))) \
            .replace("{{average_age}}", str(stats.get("average_age", 0))) \
            .replace("{{minimum_age}}", str(stats.get("minimum_age", 0))) \
            .replace("{{maximum_age}}", str(stats.get("maximum_age", 0))) \
            .replace("{{different_countries}}", str(stats.get("different_countries", 0))) \
            .replace("{{username_length_min}}", str(stats.get("username_length_stats", {}).get("min", 0))) \
            .replace("{{username_length_max}}", str(stats.get("username_length_stats", {}).get("max", 0))) \
            .replace("{{username_length_avg}}", str(stats.get("username_length_stats", {}).get("average", 0))) \
            .replace("{{timestamp}}", self.timestamp) \
            .replace("{{country_labels}}", json.dumps(country_labels)) \
            .replace("{{country_counts_list}}", json.dumps(country_counts_list)) \
            .replace("{{country_colors}}", json.dumps(country_colors)) \
            .replace("{{gender_labels}}", json.dumps(gender_labels)) \
            .replace("{{gender_counts_list}}", json.dumps(gender_counts_list)) \
            .replace("{{age_decade_labels}}", json.dumps(age_decade_labels)) \
            .replace("{{age_decade_counts}}", json.dumps(age_decade_counts)) \
            .replace("{{age_decade_colors}}", json.dumps(age_decade_colors)) \
            .replace("{{user_rows}}", user_rows) \
            .replace("{{password_length_keys}}",
                     json.dumps(list(stats['password_length_stats']['distribution'].keys()))) \
            .replace("{{password_length_values}}",
                     json.dumps(list(stats['password_length_stats']['distribution'].values()))) \
            .replace("{{lowercase_only}}", str(stats['password_complexity_stats'].get('lowercase_only', 0))) \
            .replace("{{numbers_only}}", str(stats['password_complexity_stats'].get('numbers_only', 0))) \
            .replace("{{letters_and_numbers}}", str(stats['password_complexity_stats'].get('letters_and_numbers', 0))) \
            .replace("{{includes_symbols}}", str(stats['password_complexity_stats'].get('includes_symbols', 0))) \
            .replace("{{top_passwords_labels}}", json.dumps([p['password'] for p in stats['password_pattern_stats']])) \
            .replace("{{top_passwords_counts}}", json.dumps([p['count'] for p in stats['password_pattern_stats']])) \
            .replace("{{short_password_percent}}", str(short_password_percent)) \
            .replace("{{strong_percent}}", str(strong_percent)) \
            .replace("{{weak_percent}}", str(weak_percent)) \
            .replace("{{name_in_password_display}}", name_in_password_display) \
            .replace("{{birthyear_in_password_display}}", birthyear_in_password_display) \
            .replace("{{name_in_password_percent}}", str(name_in_password_percent)) \
            .replace("{{birthyear_in_password_percent}}", str(birthyear_in_password_percent))

        # Save and open HTML
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(dashboard_path.resolve().as_uri())
        print("✅ Dashboard generated and opened in browser.")
        print(f"✅ Stats saved: {stats_path}")


