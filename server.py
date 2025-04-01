from flask import Flask, request, jsonify
from flask_cors import CORS  # 👈 Importa CORS
from eva_llama_14 import EVA

app = Flask(__name__)
CORS(app)  # 👈 Habilita CORS para TODAS las rutas

assistant = EVA()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'response': 'No se recibió ningún mensaje.'}), 400

    response = assistant.chat(user_message)
    if not response:
        response = "Lo siento, no tengo una respuesta en este momento."

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)

