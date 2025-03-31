from flask import Flask, request, jsonify
from eva_llama_backend.eva_llama_14 import EvaAssistant

app = Flask(__name__)
eva = EvaAssistant()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Falta el mensaje"}), 400

    response = eva.ollama_client.generate_response(message)
    return jsonify({"response": response})

@app.route("/", methods=["GET"])
def home():
    return "Asistente EVA está corriendo con Render 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
