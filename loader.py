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
        self.template_path = Path(__file__).parent / "templates" / "dashboard_template.html"

    def save_stats_and_dashboard(self, users_processed: list, stats: dict):
        """Save statistics to JSON and generate HTML dashboard."""
        processed_json_path = self.output_dir / "processed_users.json"
        with open(processed_json_path, "w", encoding="utf-8") as f:
            json.dump(users_processed, f, indent=4)
        print(f"Processed users saved to: {processed_json_path}")

        stats_json_path = self.output_dir / "statistics.json"
        with open(stats_json_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4)
        print(f"Stats saved: {stats_json_path}")

        dashboard_path = self.output_dir / "dashboard.html"

        if not self.template_path.exists():
            print(f"Error: Dashboard template not found at {self.template_path}")
            return

        success = self._generate_html_dashboard(dashboard_path, stats)

        if success:
            print(f"Dashboard generated and saved to: {dashboard_path}")
            try:
                webbrowser.open_new_tab(f"file://{dashboard_path.resolve()}")
            except Exception:
                print("(Skipping browser open on server)")
        else:
            print("Failed to generate dashboard. Skipping browser open.")

    def _create_chart_js_script(self, stats: dict) -> str:
        """Generates the JavaScript <script> block for Chart.js with coherent colors and layout."""
        blue_main = "#3B82F6"
        blue_light = "#60A5FA"
        blue_dark = "#1D4ED8"
        pink_soft = "#F472B6"
        green_soft = "#10B981"
        orange_soft = "#F59E0B"
        red_soft = "#EF4444"
        grid_color = "#E6EEF9"

        count_tooltip_callback = """
        tooltip: {
            callbacks: {
                label: function(context) {
                    let label = context.label || '';
                    let value = context.raw !== undefined ? context.raw : (context.parsed ? context.parsed.y : 0);
                    return ` ${label}: ${value}`;
                }
            }
        },
        """

        gender_labels = list(stats.get("gender_distribution", {}).keys())
        gender_data = list(stats.get("gender_distribution", {}).values())
        gender_script = f"""
        (function(){{
            const ctx = document.getElementById('genderChart').getContext('2d');
            new Chart(ctx, {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(gender_labels)},
                    datasets: [{{
                        data: {json.dumps(gender_data)},
                        backgroundColor: ['{blue_main}', '{pink_soft}'],
                        borderColor: '#FFFFFF',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ {count_tooltip_callback} legend: {{ position: 'top', align: 'center' }} }},
                    layout: {{ padding: 8 }}
                }}
            }});
        }})();
        """

        age_data = stats.get("age_decade_distribution", {})
        age_labels = sorted(age_data.keys())
        age_values = [age_data[k] for k in age_labels]
        age_script = f"""
        (function(){{
            const ctx = document.getElementById('ageChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(age_labels)},
                    datasets: [{{
                        label: 'Users',
                        data: {json.dumps(age_values)},
                        backgroundColor: '{blue_light}',
                        borderColor: '{blue_main}',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }}, {count_tooltip_callback} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{
                            beginAtZero: true,
                            grid: {{ color: '{grid_color}' }}
                        }}
                    }},
                    layout: {{ padding: 6 }}
                }}
            }});
        }})();
        """

        country_data = stats.get("users_per_country", {})
        top_10 = sorted(country_data.items(), key=lambda x: x[1], reverse=True)[:10]
        country_labels = [c[0] for c in top_10]
        country_values = [c[1] for c in top_10]
        country_script = f"""
        (function(){{
            const ctx = document.getElementById('countryChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(country_labels)},
                    datasets: [{{
                        label: 'User Count',
                        data: {json.dumps(country_values)},
                        backgroundColor: '{blue_main}',
                        borderRadius: 6,
                        barThickness: 18
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }}, {count_tooltip_callback} }},
                    scales: {{
                        x: {{ grid: {{ color: '{grid_color}' }}, beginAtZero: true }},
                        y: {{ grid: {{ display: false }} }}
                    }},
                    layout: {{ padding: 8 }}
                }}
            }});
        }})();
        """

        # --- PASSWORD COMPLEXITY (doughnut) ---
        comp_data = stats.get("password_complexity_stats", {})
        comp_labels = [k.replace("_", " ").title() for k in comp_data.keys()]
        comp_values = list(comp_data.values())
        # If there are more labels than colors, Chart.js will cycle the colors — that's OK.
        complexity_colors = [green_soft, blue_main, orange_soft, red_soft]
        comp_colors_js = json.dumps(complexity_colors)
        pass_comp_script = f"""
        (function(){{
            const ctx = document.getElementById('passComplexityChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(comp_labels)},
                    datasets: [{{
                        data: {json.dumps(comp_values)},
                        backgroundColor: {comp_colors_js},
                        borderColor: '#FFFFFF',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'top', labels: {{ boxWidth: 12 }} }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.label || '';
                                    let value = context.raw || 0;
                                    let total = 0;
                                    context.chart.data.datasets[0].data.forEach(n => total += Number(n || 0));
                                    let pct = total ? (value / total * 100).toFixed(1) : '0.0';
                                    return ` ${{label}}: ${{value}} (${{pct}}%)`;
                                }}
                            }}
                        }}
                    }},
                    layout: {{ padding: 6 }}
                }}
            }});
        }})();
        """

        pass_len_data = stats.get("password_length_stats", {}).get("distribution", {})
        pass_len_sorted = sorted(pass_len_data.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else x[0])
        pass_len_labels = [item[0] for item in pass_len_sorted]
        pass_len_values = [item[1] for item in pass_len_sorted]
        pass_len_script = f"""
        (function(){{
            const ctx = document.getElementById('passLengthChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(pass_len_labels)},
                    datasets: [{{
                        label: 'Count',
                        data: {json.dumps(pass_len_values)},
                        backgroundColor: '{blue_main}',
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }}, {count_tooltip_callback} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ beginAtZero: true, grid: {{ color: '{grid_color}' }} }}
                    }},
                    layout: {{ padding: 6 }}
                }}
            }});
        }})();
        """

        reg_data = stats.get("registration_by_year", {})
        reg_labels = list(reg_data.keys())
        reg_values = list(reg_data.values())
        reg_year_script = f"""
        (function(){{
            const ctx = document.getElementById('regYearChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(reg_labels)},
                    datasets: [{{
                        label: 'Users Registered',
                        data: {json.dumps(reg_values)},
                        borderColor: '{blue_main}',
                        backgroundColor: '{blue_light}',
                        tension: 0.25,
                        fill: true,
                        pointBackgroundColor: '{blue_dark}',
                        pointBorderColor: '#FFFFFF',
                        pointRadius: 4,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }}, {count_tooltip_callback} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ beginAtZero: true, grid: {{ color: '{grid_color}' }} }}
                    }},
                    layout: {{ padding: 6 }}
                }}
            }});
        }})();
        """

        tz_data = stats.get("timezone_distribution", {})
        tz_labels = [f"UTC {k}" for k in tz_data.keys()]
        tz_values = list(tz_data.values())
        timezone_script = f"""
        (function(){{
            const ctx = document.getElementById('timezoneChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(tz_labels)},
                    datasets: [{{
                        label: 'Timezone Count',
                        data: {json.dumps(tz_values)},
                        backgroundColor: '{blue_main}',
                        borderRadius: 6,
                        barThickness: 14
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }}, {count_tooltip_callback} }},
                    scales: {{
                        x: {{ grid: {{ color: '{grid_color}' }}, beginAtZero: true }},
                        y: {{ grid: {{ display: false }} }}
                    }},
                    layout: {{ padding: 6 }}
                }}
            }});
        }})();
        """

        return f"""
        <script>
        document.addEventListener("DOMContentLoaded", function() {{
            try {{
                {gender_script}
                {age_script}
                {country_script}
                {pass_comp_script}
                {pass_len_script}
                {reg_year_script}
                {timezone_script}
            }} catch (e) {{
                console.error("Error rendering charts:", e);
            }}
        }});
        </script>
        """

    def _generate_html_dashboard(self, output_path: Path, stats: dict) -> bool:
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            html_content = html_content.replace("{{TOTAL_USERS}}", str(stats.get("total_users", "N/A")))
            html_content = html_content.replace("{{AVG_AGE}}", str(stats.get("average_age", "N/A")))
            html_content = html_content.replace("{{MOST_FREQUENT_GENDER}}", str(stats.get("most_frequent_gender", "N/A")))
            html_content = html_content.replace("{{DIFFERENT_COUNTRIES}}", str(stats.get("different_countries", "N/A")))
            html_content = html_content.replace("{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            pass_len_stats = stats.get("password_length_stats", {})
            html_content = html_content.replace("{{AVG_PASSWORD_LENGTH}}", str(pass_len_stats.get("average", "N/A")))

            pass_strength_stats = stats.get("password_strength", {})
            strong_percent = pass_strength_stats.get("percent_strong", "N/A")
            strong_count = pass_strength_stats.get("strong", "N/A")
            html_content = html_content.replace("{{PASSWORD_STRENGTH_SUMMARY}}", f"{strong_percent}% ({strong_count})")

            name_stats = stats.get("name_in_password", {})
            html_content = html_content.replace("{{NAME_IN_PASSWORD}}", f"{name_stats.get('count', 0)} / {name_stats.get('total', 0)}")

            bday_stats = stats.get("birthyear_in_password", {})
            html_content = html_content.replace("{{BIRTHYEAR_IN_PASSWORD}}", f"{bday_stats.get('count', 0)} / {bday_stats.get('total', 0)}")

            user_stats = stats.get("username_in_password", {})
            html_content = html_content.replace("{{USERNAME_IN_PASSWORD}}", f"{user_stats.get('count', 0)} / {user_stats.get('total', 0)}")

            html_content = html_content.replace("{{PASS_LEN_MIN}}", str(pass_len_stats.get("min", "N/A")))
            html_content = html_content.replace("{{PASS_LEN_MAX}}", str(pass_len_stats.get("max", "N/A")))

            html_content = html_content.replace("{{MOST_SECURE_PASSWORD}}", str(stats.get("most_secure_password", "N/A")))

            top_pass_list = stats.get("password_pattern_stats", [])
            if top_pass_list:
                top = top_pass_list[:10]
                rows = ""
                for i, item in enumerate(top, 1):
                    pwd = item.get("password", "")
                    cnt = item.get("count", 0)
                    rows += f"""
                        <tr>
                            <td class="t-idx">{i}</td>
                            <td class="t-pwd">{pwd}</td>
                            <td class="t-count">{cnt}</td>
                        </tr>
                    """
                top_pass_html = f"""
                    <div class="top-pass-table-wrap">
                        <table class="top-pass-table">
                            <thead>
                                <tr><th>#</th><th>Password</th><th>Count</th></tr>
                            </thead>
                            <tbody>
                                {rows}
                            </tbody>
                        </table>
                    </div>
                """
            else:
                top_pass_html = "<p>No password data available.</p>"

            html_content = html_content.replace("{{TOP_PASSWORDS_TABLE}}", top_pass_html)

            html_content = html_content.replace("{{VALID_CSV_PATH}}", "valid_users.csv.enc")
            html_content = html_content.replace("{{INVALID_CSV_PATH}}", "invalid_users.csv.enc")
            html_content = html_content.replace("{{STATS_JSON_PATH}}", "statistics.json")

            chart_script = self._create_chart_js_script(stats)
            html_content = html_content.replace("{{CHART_JS_SCRIPT}}", chart_script)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return True

        except Exception as e:
            print(f"Error generating dashboard: {e}")
            return False