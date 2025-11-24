from flask import Flask, render_template_string, request, jsonify
import sqlite3  # <-- Usamos esto en lugar de psycopg2 para local

app = Flask(__name__)


# --- RUTA PRINCIPAL ---
@app.route('/')
def home():
    # Leemos el HTML
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return "<h1>Error: No se encuentra el archivo dashboard.html</h1>"

    # Simulamos los datos del ETL
    content = content.replace('{{TOTAL_USERS}}', 'LOCAL_TEST')
    content = content.replace('{{DIFFERENT_COUNTRIES}}', '10')
    # (Puedes añadir el resto de replaces aquí)

    return render_template_string(content)


# --- RUTA PARA GUARDAR DATOS (Simulando RDS) ---
@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    password_to_save = data.get('password')

    try:
        # Conectamos a un archivo local 'demo.db'
        # Si no existe, se crea solo.
        conn = sqlite3.connect('demo.db')
        cur = conn.cursor()

        # Crear tabla si no existe
        cur.execute("CREATE TABLE IF NOT EXISTS demo_passwords (id INTEGER PRIMARY KEY, pass_text TEXT)")

        # Guardar el dato
        cur.execute("INSERT INTO demo_passwords (pass_text) VALUES (?)", (password_to_save,))

        conn.commit()
        conn.close()

        print(f"--> Dato guardado en local: {password_to_save}")  # Para que lo veas en la terminal
        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


if __name__ == '__main__':
    # Corremos en localhost puerto 5000
    print("Abriendo servidor en http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)