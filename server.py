from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant, CONFIG
from datetime import datetime
import os
import psycopg2

app = Flask(__name__)
CORS(app)

# Diccionario para mantener instancias EVA por sesión
eva_instances = {}

# Función para guardar en PostgreSQL
def guardar_en_postgres(rol, mensaje):
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                id SERIAL PRIMARY KEY,
                rol TEXT,
                mensaje TEXT,
                fecha TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        cur.execute("INSERT INTO conversaciones (rol, mensaje) VALUES (%s, %s)", (rol, mensaje))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[DB] Guardado en PostgreSQL: {rol} → {mensaje}")
        return True
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
        session_id = data.get("sessionId", "default")

        # Crear o recuperar instancia de EVA
        if session_id not in eva_instances:
            CONFIG["max_response_length"] = 300
            CONFIG["short_response_length"] = 200
            CONFIG["show_typing"] = False
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)

        eva = eva_instances[session_id]
        response = eva.get_response(user_message)

        # Si Ollama falla y no hay respuesta
        if not response:
            response = "Lo siento, en este momento no puedo responder. ¿Podrías intentarlo más tarde o escribirnos a contacto@antaresinnovate.com?"

        # Guardar en base de datos
        guardar_en_postgres("usuario", user_message)
        guardar_en_postgres("asistente", response)

        return jsonify({
            "message": user_message,
            "response": response,
            "sessionId": session_id
        })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/reiniciar", methods=["POST"])
def reiniciar_instancia():
    try:
        data = request.get_json()
        session_id = data.get("sessionId", "default")

        CONFIG["max_response_length"] = 300
        CONFIG["short_response_length"] = 200

        eva_instances[session_id] = EvaAssistant(typing_simulation=False)

        return jsonify({"status": "success", "message": "Eva reiniciada correctamente"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
