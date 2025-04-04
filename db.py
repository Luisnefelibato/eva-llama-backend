import psycopg2
from datetime import datetime

# Datos de conexión a la base de datos de Render
DB_HOST = "dpg-cvllj3t6ubrc73f0ia50-a.oregon-postgres.render.com"
DB_NAME = "eva_db_27qk"
DB_USER = "eva_db_27qk_user"
DB_PASSWORD = "71GbjXoWwczOJ3frkcE8Iq4j6Yl5A5Vy"
DB_PORT = "5432"

# Conexión global (reutilizable)
def obtener_conexion():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode="require"
    )

# Función para guardar conversaciones
def guardar_conversacion(rol: str, mensaje: str, session_id: str = "default"):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        query = """
            INSERT INTO conversaciones (fecha, rol, mensaje, session_id)
            VALUES (CURRENT_TIMESTAMP, %s, %s, %s)
        """
        cursor.execute(query, (rol, mensaje, session_id))
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR DB] {e}")
