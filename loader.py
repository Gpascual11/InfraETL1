# ===============================
# CLASS 3: LOADER
# ===============================

import json
from pathlib import Path
import webbrowser
from datetime import datetime


class Loader:
    """
    Loader class:
    - Saves transformed data to a JSON file.
    - Generates and displays an HTML dashboard from a template.
    """

    def __init__(self, source: list, output_dir: Path):
        self.source = source
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Build a path to the template file relative to this .py file
        self.template_path = Path(__file__).parent / "templates" / "dashboard_template.html"

    def save_stats_and_dashboard(self, users_processed: list, stats: dict):
        """Save statistics to JSON and generate HTML dashboard."""

        # Save raw processed data
        processed_json_path = self.output_dir / "processed_users.json"
        with open(processed_json_path, "w", encoding="utf-8") as f:
            json.dump(users_processed, f, indent=4)
        print(f"Processed users saved to: {processed_json_path}")

        # Save statistics to JSON
        stats_json_path = self.output_dir / "statistics.json"
        with open(stats_json_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4)
        print(f"Stats saved: {stats_json_path}")

        # Generate HTML Dashboard
        dashboard_path = self.output_dir / "dashboard.html"

        # Check if dashboard generation was successful
        success = self._generate_html_dashboard(dashboard_path, stats)

        if success:
            print(f"Dashboard generated and saved to: {dashboard_path}")
            webbrowser.open_new_tab(f"file://{dashboard_path.resolve()}")
        else:
            print(f"Failed to generate dashboard. Skipping browser open.")

    def _create_chart_js_script(self, stats: dict) -> str:
        """Generates the JavaScript <script> block for Chart.js."""

        # Chart Colors
        color1 = "#74B8C1"
        color2 = "#B0D0D3"
        color3 = "#E0EFEB"

        # Tooltip Helper Callback
        # This function is reused by multiple charts to show "Count: X"
        count_tooltip_callback = """
        tooltip: {
            callbacks: {
                label: function(tooltipItem) {
                    let label = tooltipItem.label || '';
                    let value = tooltipItem.raw || 0;
                    return ` ${label}: Count ${value}`;
                }
            }
        },
        """

        # 1. Gender Chart (Pie)
        gender_labels = list(stats.get("gender_distribution", {}).keys())
        gender_data = list(stats.get("gender_distribution", {}).values())
        gender_script = f"""
        new Chart(document.getElementById('genderChart'), {{
            type: 'pie',
            data: {{
                labels: {json.dumps(gender_labels)},
                datasets: [{{
                    data: {json.dumps(gender_data)},
                    backgroundColor: ['{color1}', '{color2}', '{color3}'],
                }}]
            }},
            options: {{ 
                responsive: true, 
                maintainAspectRatio: true,
                plugins: {{ {count_tooltip_callback} }}
            }}
        }});
        """

        # 2. Age Decade Chart (Bar)
        age_data = stats.get("age_decade_distribution", {})
        age_labels = sorted(age_data.keys())
        age_values = [age_data[k] for k in age_labels]
        age_script = f"""
        new Chart(document.getElementById('ageChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(age_labels)},
                datasets: [{{
                    label: 'User Count',
                    data: {json.dumps(age_values)},
                    backgroundColor: '{color2}',
                    borderColor: '{color1}',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ 
                    legend: {{ display: false }},
                    {count_tooltip_callback}
                }},
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
        """

        # 3. Country Chart (Horizontal Bar)
        country_data = stats.get("users_per_country", {})
        top_10_countries = sorted(country_data.items(), key=lambda x: x[1], reverse=True)[:10]
        country_labels = [c[0] for c in top_10_countries]
        country_values = [c[1] for c in top_10_countries]
        country_script = f"""
        new Chart(document.getElementById('countryChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(country_labels)},
                datasets: [{{
                    label: 'User Count',
                    data: {json.dumps(country_values)},
                    backgroundColor: '{color1}',
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                plugins: {{ 
                    legend: {{ display: false }},
                    {count_tooltip_callback}
                }}
            }}
        }});
        """

        # 4. Email Domain Chart (Horizontal Bar)
        email_data = stats.get("email_domain_distribution", {})
        top_10_emails = sorted(email_data.items(), key=lambda x: x[1], reverse=True)[:10]
        email_labels = [e[0] for e in top_10_emails]
        email_values = [e[1] for e in top_10_emails]
        email_script = f"""
        new Chart(document.getElementById('emailChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(email_labels)},
                datasets: [{{
                    label: 'Domain Count',
                    data: {json.dumps(email_values)},
                    backgroundColor: '{color2}',
                    borderColor: '{color1}',
                    borderWidth: 1
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                plugins: {{ 
                    legend: {{ display: false }},
                    {count_tooltip_callback}
                }}
            }}
        }});
        """

        # 5. Password Complexity (Doughnut)
        comp_data = stats.get("password_complexity_stats", {})
        comp_labels = [k.replace("_", " ").title() for k in comp_data.keys()]
        comp_values = list(comp_data.values())
        comp_total = sum(comp_values) if sum(comp_values) > 0 else 1  # Avoid division by zero

        pass_comp_script = f"""
        new Chart(document.getElementById('passComplexityChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(comp_labels)},
                datasets: [{{
                    data: {json.dumps(comp_values)},
                    backgroundColor: ['{color1}', '{color2}', '{color3}', '#A7C7C6'],
                }}]
            }},
            options: {{ 
                responsive: true, 
                plugins: {{ 
                    legend: {{ position: 'top' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(tooltipItem) {{
                                let label = tooltipItem.label || '';
                                let rawValue = tooltipItem.raw || 0;
                                let percentage = (rawValue / {comp_total}) * 100;
                                return ` ${{label}}: ${{rawValue}} (${{percentage.toFixed(1)}}%)`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
        """

        # 6. Password Length Chart (Bar)
        pass_len_data = stats.get("password_length_stats", {}).get("distribution", {})
        pass_len_sorted = sorted(pass_len_data.items(), key=lambda x: int(x[0]))
        pass_len_labels = [item[0] for item in pass_len_sorted]
        pass_len_values = [item[1] for item in pass_len_sorted]

        pass_len_script = f"""
        new Chart(document.getElementById('passLengthChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(pass_len_labels)},
                datasets: [{{
                    label: 'Password Length Count',
                    data: {json.dumps(pass_len_values)},
                    backgroundColor: '{color1}',
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ 
                    legend: {{ display: false }},
                    {count_tooltip_callback}
                }},
                scales: {{ 
                    x: {{ title: {{ display: true, text: 'Password Length' }} }},
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Count' }} }}
                }}
            }}
        }});
        """

        # 7. Registration by Year (Line Chart)
        reg_data = stats.get("registration_by_year", {})
        reg_labels = list(reg_data.keys())
        reg_values = list(reg_data.values())

        reg_year_script = f"""
        new Chart(document.getElementById('regYearChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(reg_labels)},
                datasets: [{{
                    label: 'Users Registered',
                    data: {json.dumps(reg_values)},
                    backgroundColor: '{color2}',
                    borderColor: '{color1}',
                    borderWidth: 2,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ 
                    legend: {{ display: false }},
                    {count_tooltip_callback}
                }},
                scales: {{ 
                    x: {{ title: {{ display: true, text: 'Year' }} }},
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Count' }} }}
                }}
            }}
        }});
        """

        # 8. Timezone Distribution (Horizontal Bar)
        tz_data = stats.get("timezone_distribution", {})
        tz_labels = [f"UTC {k}" for k in tz_data.keys()]
        tz_values = list(tz_data.values())

        timezone_script = f"""
        new Chart(document.getElementById('timezoneChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(tz_labels)},
                datasets: [{{
                    label: 'Timezone Count',
                    data: {json.dumps(tz_values)},
                    backgroundColor: '{color1}',
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                plugins: {{ 
                    legend: {{ display: false }},
                    {count_tooltip_callback}
                }}
            }}
        }});
        """

        return f"""
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                try {{
                    {gender_script}
                    {age_script}
                    {country_script}
                    {email_script}
                    {pass_comp_script}
                    {pass_len_script}
                    {reg_year_script}
                    {timezone_script}
                }} catch (e) {{
                    console.error("Error rendering charts: ", e);
                }}
            }});
        </script>
        """

    def _generate_html_dashboard(self, output_path: Path, stats: dict) -> bool:
        """
        Generates an HTML dashboard by populating a template file.
        Returns True on success, False on failure.
        """

        if not self.template_path.exists():
            print(f"Error: dashboard_template.html not found.")
            print(f"   (Looking for it at: {self.template_path.resolve()})")
            return False

        with open(self.template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # 1. Fill General Stats
        html_content = html_content.replace("{{TOTAL_USERS}}", str(stats.get("total_users", "N/A")))
        html_content = html_content.replace("{{AVG_AGE}}", str(stats.get("average_age", "N/A")))
        html_content = html_content.replace("{{MOST_FREQUENT_GENDER}}", str(stats.get("most_frequent_gender", "N/A")))
        html_content = html_content.replace("{{DIFFERENT_COUNTRIES}}", str(stats.get("different_countries", "N/A")))

        # 2. Fill Password Stats
        html_content = html_content.replace("{{AVG_PASSWORD_LENGTH}}",
                                            str(stats.get("password_length_stats", {}).get("average", "N/A")))

        pass_strength_stats = stats.get("password_strength", {})
        strong_percent = pass_strength_stats.get("percent_strong", "N/A")
        strong_count = pass_strength_stats.get("strong", "N/A")
        total_users = pass_strength_stats.get("total_users", "N/A")
        pass_summary_str = f"{strong_percent}% ({strong_count} / {total_users})"
        html_content = html_content.replace("{{PASSWORD_STRENGTH_SUMMARY}}", pass_summary_str)

        name_stats = stats.get("name_in_password", {})
        html_content = html_content.replace("{{NAME_IN_PASSWORD}}",
                                            f"{name_stats.get('count', 'N/A')} / {name_stats.get('total', 'N/A')}")

        bday_stats = stats.get("birthyear_in_password", {})
        html_content = html_content.replace("{{BIRTHYEAR_IN_PASSWORD}}",
                                            f"{bday_stats.get('count', 'N/A')} / {bday_stats.get('total', 'N/A')}")

        user_in_pass_stats = stats.get("username_in_password", {})
        html_content = html_content.replace("{{USERNAME_IN_PASSWORD}}",
                                            f"{user_in_pass_stats.get('count', 'N/A')} / {user_in_pass_stats.get('total', 'N/A')}")

        # Format Top 10 Passwords for the <pre> tag
        top_pass = stats.get("password_pattern_stats", [])
        top_pass_str = "\n".join([f"Count: {item['count']:<4} | Pass: {item['password']}" for item in top_pass])
        if not top_pass_str:
            top_pass_str = "No common passwords found."
        html_content = html_content.replace("{{TOP_PASSWORDS_TABLE}}", top_pass_str)

        # 3. Fill Download Links
        # These are relative to the dashboard.html file
        html_content = html_content.replace("{{VALID_CSV_PATH}}", "valid_users.csv.enc")
        html_content = html_content.replace("{{INVALID_CSV_PATH}}", "invalid_users.csv.enc")
        html_content = html_content.replace("{{KEY_PATH}}", "encryption_key.key")
        html_content = html_content.replace("{{STATS_JSON_PATH}}", "statistics.json")

        # 4. Fill Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = html_content.replace("{{TIMESTAMP}}", timestamp)

        # 5. Inject Chart.js Script
        chart_script = self._create_chart_js_script(stats)
        html_content = html_content.replace("{{CHART_JS_SCRIPT}}", chart_script)

        # 6. Write the final file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return True