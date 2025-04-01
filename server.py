from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Instancia del asistente
assistant = EvaAssistant()

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

        # Generar respuesta con Ollama
        response = assistant.ollama_client.generate_response(user_message)

        if not response:
            response = "Lo siento, no tengo una respuesta en este momento."

        return jsonify({
            "message": user_message,
            "response": response
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
