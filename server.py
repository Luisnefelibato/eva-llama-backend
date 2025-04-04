from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant, CONFIG
from db import guardar_conversacion  # Importamos la función existente
import os
import re

app = Flask(__name__)
CORS(app)

# Diccionario para mantener instancias por sesión
eva_instances = {}

def es_pregunta_tecnica(mensaje):
    """Determina si el mensaje es una pregunta técnica que requiere respuesta detallada"""
    mensaje_lower = mensaje.lower()
    
    # Palabras clave técnicas
    tecnicas = [
        "como", "implementar", "desarrollar", "código", "programar", 
        "automatizar", "integrar", "optimizar", "configurar", "api",
        "base de datos", "framework", "javascript", "python", "react", 
        "arquitectura", "tecnología", "servidor", "cloud", "desplegar"
    ]
    
    # Verificar si tiene palabras técnicas
    tiene_tecnicas = any(palabra in mensaje_lower for palabra in tecnicas)
    
    # Verificar si es una pregunta compleja (longitud o estructura)
    es_compleja = len(mensaje.split()) > 10
    
    return tiene_tecnicas and es_compleja

def ajustar_configuracion_para_mensaje(mensaje):
    """Ajusta la configuración de Eva según el tipo de mensaje"""
    if es_pregunta_tecnica(mensaje):
        # Para preguntas técnicas: respuestas más largas y detalladas
        CONFIG["max_response_length"] = 500
        CONFIG["short_response_length"] = 350
    else:
        # Para preguntas simples: respuestas concisas
        CONFIG["max_response_length"] = 250
        CONFIG["short_response_length"] = 150

def optimizar_historial_conversacion(eva_instance):
    """Optimiza el historial de conversación para reducir tamaño del prompt"""
    if len(eva_instance.conversation_history) > 6:
        # Mantener solo los últimos 3 intercambios (6 mensajes)
        eva_instance.conversation_history = eva_instance.conversation_history[-6:]

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

        # Ajustar configuración según el tipo de mensaje
        ajustar_configuracion_para_mensaje(user_message)

        # Crear instancia de Eva por sesión si no existe
        if session_id not in eva_instances:
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)

        eva = eva_instances[session_id]
        
        # Optimizar historial para evitar prompts demasiado largos
        optimizar_historial_conversacion(eva)

        # Generar respuesta usando EvaAssistant
        response = eva.get_response(user_message)

        # Guardar conversación en la base de datos
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