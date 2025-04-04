from flask import Flask, request, jsonify
from flask_cors import CORS
from eva_llama_14 import EvaAssistant, CONFIG
from db import guardar_conversacion
import os
import re

app = Flask(__name__)
CORS(app)

# Diccionario para mantener instancias por sesión
eva_instances = {}

def limpiar_mensaje(mensaje):
    """
    Limpia el mensaje para evitar problemas de formato en conversaciones
    Elimina prefijos como "Asistente:" o "Usuario:" para evitar confusión
    """
    # Patrones comunes que podrían causar confusión
    patrones = [
        r'^Asistente:\s*',
        r'^Eva:\s*',
        r'^Usuario:\s*',
        r'Asistente:\s*$',
        r'Eva:\s*$',
        r'Usuario:\s*$',
    ]
    
    mensaje_limpio = mensaje
    for patron in patrones:
        mensaje_limpio = re.sub(patron, '', mensaje_limpio, flags=re.IGNORECASE)
    
    # Si el mensaje contiene una conversación completa, extraer solo la última parte
    if "Usuario:" in mensaje and "Asistente:" in mensaje:
        partes = re.split(r'Usuario:|Asistente:', mensaje)
        if partes:
            # Tomar la última parte significativa
            mensaje_limpio = partes[-1].strip()
    
    return mensaje_limpio

def ajustar_configuracion_para_mensaje(mensaje):
    """Ajusta la configuración de Eva según el tipo de mensaje"""
    # Detectar si es una pregunta técnica o compleja
    es_tecnica = any(palabra in mensaje.lower() for palabra in [
        "como", "implementar", "desarrollar", "código", "programar", 
        "automatizar", "integrar", "optimizar", "configurar"
    ])
    
    # Ajustar longitud de respuesta según complejidad
    if es_tecnica or len(mensaje.split()) > 15:
        CONFIG["max_response_length"] = 400  # Respuestas más largas para preguntas técnicas
        CONFIG["short_response_length"] = 250
    else:
        CONFIG["max_response_length"] = 250  # Respuestas más concisas para preguntas simples
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

        # Limpiar y procesar el mensaje del usuario
        mensaje_original = data["message"]
        user_message = limpiar_mensaje(mensaje_original)
        
        # Si el mensaje está vacío después de limpiarlo
        if not user_message.strip():
            user_message = mensaje_original
        
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

        # Guardar conversación
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