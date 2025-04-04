from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant, CONFIG
from db import guardar_conversacion  # Asegúrate de tener esto implementado
import os

app = Flask(__name__)
CORS(app)

# Diccionario para mantener instancias por sesión
eva_instances = {}

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

        # Crear instancia de Eva por sesión si no existe
        if session_id not in eva_instances:
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)

        eva = eva_instances[session_id]

        # ✅ Generar respuesta usando EvaAssistant
        response = eva.get_response(user_message)

        # ✅ Guardar conversación (opcional: si tenés PostgreSQL o SQLite)
        try:
            guardar_conversacion("usuario", user_message, session_id)
            guardar_conversacion("asistente", response, session_id)
        except Exception as db_error:
            print(f"[ERROR DB] {db_error}")

        return jsonify({
            "message": user_message,
            "response": response,
            "sessionId": session_id
        })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    try:
        data = request.get_json()
        session_id = data.get("sessionId", "default")

        eva_instances[session_id] = EvaAssistant(typing_simulation=False)

        return jsonify({"status": "ok", "message": "Eva reiniciada correctamente"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
