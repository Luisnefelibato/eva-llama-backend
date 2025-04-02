import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    "host": "dpg-cvllj3t6ubrc73f0ia50-a",
    "port": 5432,
    "dbname": "eva_db_27qk",
    "user": "eva_db_27qk_user",
    "password": "71GbjXoWwczOJ3frkcE8Iq4j6Yl5A5Vy"
}

def guardar_conversacion(rol, mensaje):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO conversaciones (fecha, rol, mensaje)
            VALUES (%s, %s, %s)
        """, (datetime.now(), rol, mensaje))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR DB] {e}")
