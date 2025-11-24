import psycopg2

DB_HOST = "YOUR_HOST"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "YOUR_PASSWORD"

try:
    print(f"conectando a {DB_HOST}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=10
    )
    cur = conn.cursor()

    cur.execute("SELECT * FROM secrets;")
    rows = cur.fetchall()

    print(f"\n✅ CONEXIÓN ÉXITOSA - Se encontraron {len(rows)} registros:\n")
    print(f"{'ID':<5} | {'FECHA':<20} | {'CONTRASEÑA/SECRETO'}")
    print("-" * 50)

    for row in rows:
        id_db = row[0]
        content = row[1]
        timestamp = row[2]
        print(f"{id_db:<5} | {str(timestamp)[:19]:<20} | {content}")

    cur.close()
    conn.close()

except Exception as e:
    print("\nERROR DE CONEXIÓN:")
    print(e)
    print("\nCONSEJO: Revisa el Security Group de tu RDS en AWS y añade 'My IP'.")