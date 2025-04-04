from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant, CONFIG
from db import guardar_conversacion  # ✅ Importar desde db.py

app = Flask(__name__)
CORS(app)

# Diccionario de sesiones EVA activas
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

        # Inicializa Eva si no existe para esta sesión
        if session_id not in eva_instances:
            CONFIG["max_response_length"] = 300
            CONFIG["short_response_length"] = 200
            CONFIG["show_typing"] = False
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)

        eva = eva_instances[session_id]
        response = eva.get_response(user_message)

        # Si Ollama falla completamente
        if not response:
            response = "Lo siento, no pude generar una respuesta en este momento. Intenta de nuevo o escríbenos a contacto@antaresinnovate.com"

        # Guardar conversación en PostgreSQL
        guardar_conversacion("usuario", user_message, session_id)
        guardar_conversacion("asistente", response, session_id)

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
        CONFIG["show_typing"] = False

        eva_instances[session_id] = EvaAssistant(typing_simulation=False)

        return jsonify({"status": "success", "message": "Eva reiniciada correctamente"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
