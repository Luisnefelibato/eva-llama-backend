from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant, CONFIG
import sqlite3
from datetime import datetime
import psycopg2

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Diccionario para mantener instancias de Eva para diferentes sesiones
eva_instances = {}

# Función para guardar conversaciones en PostgreSQL
def guardar_en_postgres(rol, mensaje):
    try:
        from db import guardar_conversacion
        guardar_conversacion(rol, mensaje)
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
        
        # Crear o recuperar una instancia de Eva para esta sesión
        if session_id not in eva_instances:
            # Configurar Eva para que las respuestas sean concisas
            CONFIG["max_response_length"] = 300  # Respuestas más cortas
            CONFIG["short_response_length"] = 200
            CONFIG["show_typing"] = False  # Desactivar simulación de escritura
            
            # Crear una nueva instancia para esta sesión
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)
        
        # Obtener la instancia de Eva para esta sesión
        eva = eva_instances[session_id]
        
        # Generar respuesta usando la implementación completa de Eva
        response = eva.get_response(user_message)
        
        # Guardar la conversación en PostgreSQL
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
    """Reinicia la instancia de Eva para una sesión específica"""
    try:
        data = request.get_json()
        session_id = data.get("sessionId", "default")
        
        if session_id in eva_instances:
            # Configurar para respuestas concisas
            CONFIG["max_response_length"] = 300
            CONFIG["short_response_length"] = 200
            
            # Crear una nueva instancia
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)
            
            return jsonify({"status": "success", "message": "Eva reiniciada correctamente"})
        else:
            return jsonify({"status": "warning", "message": "No existía sesión previa, creando nueva"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)