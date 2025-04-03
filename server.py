from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant
from datetime import datetime
import os
import sqlite3
import psycopg2

app = Flask(__name__)
CORS(app)

assistant = EvaAssistant(typing_simulation=False)
user_sessions = {}

# Guardar en SQLite local
def guardar_conversacion(mensaje, respuesta):
    try:
        conn = sqlite3.connect("conversaciones_eva.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mensaje_usuario TEXT,
                respuesta_eva TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("INSERT INTO conversaciones (mensaje_usuario, respuesta_eva) VALUES (?, ?)", (mensaje, respuesta))
        conn.commit()
        conn.close()
    except Exception as err:
        print(f"[ERROR] No se pudo guardar la conversación (SQLite): {err}")

# Guardar en PostgreSQL si está configurado
def guardar_en_postgres(mensaje, respuesta):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[INFO] DATABASE_URL no está definido, se omite PostgreSQL.")
        return

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                id SERIAL PRIMARY KEY,
                mensaje_usuario TEXT,
                respuesta_eva TEXT,
                timestamp TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        cur.execute(
            "INSERT INTO conversaciones (mensaje_usuario, respuesta_eva) VALUES (%s, %s)",
            (mensaje, respuesta)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"[DB] Conversación guardada en PostgreSQL.")
    except Exception as e:
        print(f"[ERROR] PostgreSQL: {e}")

@app.route("/", methods=["GET"])
def home():
    return "EVA está corriendo en Render 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Falta el campo 'message' en el JSON."}), 400

        user_message = data["message"]
        session_id = data.get("sessionId", "default")

        # Crear o recuperar sesión
        if session_id not in user_sessions:
            user_sessions[session_id] = {
                "assistant": EvaAssistant(typing_simulation=False),
                "last_activity": datetime.now()
            }

        session_assistant = user_sessions[session_id]["assistant"]
        user_sessions[session_id]["last_activity"] = datetime.now()

        response = session_assistant.get_response(user_message)

        if not response:
            response = "Lo siento, no tengo una respuesta en este momento. ¿Te gustaría programar una reunión con uno de nuestros especialistas en Antares Innovate?"

        # Guardar conversación local y remota
        guardar_conversacion(user_message, response)
        guardar_en_postgres(user_message, response)

        cleanup_old_sessions()

        return jsonify({
            "message": user_message,
            "response": response,
            "sessionId": session_id
        })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500

def cleanup_old_sessions():
    """Elimina sesiones inactivas por más de 30 minutos"""
    try:
        current_time = datetime.now()
        sessions_to_remove = []
        for session_id, session_data in user_sessions.items():
            time_diff = (current_time - session_data["last_activity"]).total_seconds() / 60
            if time_diff > 30:
                sessions_to_remove.append(session_id)
        for session_id in sessions_to_remove:
            del user_sessions[session_id]
    except Exception as e:
        print(f"[ERROR] Error en limpieza de sesiones: {str(e)}")

@app.route("/reiniciar", methods=["POST"])
def reiniciar_instancia():
    """Reinicia la instancia de Eva para debug"""
    try:
        global assistant
        assistant = EvaAssistant(typing_simulation=False)
        return jsonify({"status": "success", "message": "Eva reiniciada correctamente"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
