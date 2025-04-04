from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Instancia global del asistente (se reutiliza entre solicitudes)
assistant = EvaAssistant(typing_simulation=False)

# Diccionario para mantener sesiones de usuarios
user_sessions = {}

# Función para guardar conversaciones en SQLite
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
        print(f"[ERROR] No se pudo guardar la conversación: {err}")
        
# Función para guardar también en postgres si está configurado
def guardar_en_postgres(mensaje, respuesta):
    try:
        from db import guardar_conversacion as guardar_pg
        # Guardar en PostgreSQL si está disponible
        guardar_pg("usuario", mensaje)
        guardar_pg("asistente", respuesta)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"[ERROR DB] {e}")
        return False

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
        
        # Obtener ID de sesión o crear uno nuevo
        session_id = data.get("sessionId", "default")
        
        # Recuperar o crear un asistente específico para esta sesión
        if session_id not in user_sessions:
            # Si es una nueva sesión, crear un nuevo asistente con historial limpio
            user_sessions[session_id] = {
                "assistant": EvaAssistant(typing_simulation=False),
                "last_activity": datetime.now()
            }
        
        # Obtener el asistente para esta sesión
        session_assistant = user_sessions[session_id]["assistant"]
        user_sessions[session_id]["last_activity"] = datetime.now()
        
        # Usar get_response() que tiene toda la lógica de Eva en lugar de generate_response()
        response = session_assistant.get_response(user_message)

        if not response:
            response = "Lo siento, no tengo una respuesta en este momento. ¿Te gustaría programar una reunión con uno de nuestros especialistas en Antares Innovate?"

        # Guardar conversación en SQLite
        guardar_conversacion(user_message, response)
        
        # Intentar guardar también en PostgreSQL si está disponible
        guardar_en_postgres(user_message, response)
        
        # Realizar limpieza de sesiones antiguas (más de 30 minutos sin actividad)
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
            # Si la sesión lleva más de 30 minutos sin actividad
            time_diff = (current_time - session_data["last_activity"]).total_seconds() / 60
            if time_diff > 30:
                sessions_to_remove.append(session_id)
        
        # Eliminar sesiones antiguas
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
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)