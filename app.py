from flask import Flask, render_template_string, request, jsonify
import psycopg2  # O usa 'import pymysql' si es MySQL

app = Flask(__name__)

# --- CONFIGURACIÓN RDS (Cambia esto con tus datos de AWS) ---
DB_HOST = "tu-database.cluster-cw...aws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "tupassword"


# --- RUTA PRINCIPAL (DASHBOARD) ---
@app.route('/')
def home():
    # 1. Leemos el archivo HTML
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. Reemplazamos las variables "a lo bruto" (ETL simple)
    # Aquí es donde pondrías tus datos reales de tus dataframes
    content = content.replace('{{TOTAL_USERS}}', '1,250')
    content = content.replace('{{DIFFERENT_COUNTRIES}}', '45')

    return render_template_string(content)


# --- RUTA PARA GUARDAR EN RDS ---
@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    password_to_save = data.get('password')

    try:
        # Conexión simple y directa (se abre y cierra en cada petición)
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()

        # Crea tabla si no existe (para la demo)
        cur.execute("CREATE TABLE IF NOT EXISTS demo_passwords (id SERIAL PRIMARY KEY, pass_text TEXT);")

        # Insertar
        cur.execute("INSERT INTO demo_passwords (pass_text) VALUES (%s)", (password_to_save,))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


if __name__ == '__main__':
    # Ejecutar en el puerto 80 para que se vea directo en la IP
    # Necesitas correr esto con 'sudo python3 app.py'
    app.run(host='0.0.0.0', port=80, debug=True)