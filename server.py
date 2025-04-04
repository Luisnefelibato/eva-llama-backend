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

# Configuración específica para optimizar la memoria de contexto
PRECIOS_SERVICIOS = {
    "web": "desde $3,000 USD",
    "ecommerce": "desde $5,000 USD",
    "branding": "desde $2,500 USD",
    "apps": "desde $8,000 USD",
    "marketing": "desde $1,500 USD mensual",
    "automatizacion": "desde $5,000 USD"
}

def detectar_servicio_requerido(mensaje):
    """Detecta el servicio que el usuario está solicitando"""
    mensaje_lower = mensaje.lower()
    
    if any(s in mensaje_lower for s in ["pagina web", "página web", "sitio web", "web", "website"]):
        return "web"
    elif any(s in mensaje_lower for s in ["tienda", "ecommerce", "e-commerce", "vender"]):
        return "ecommerce"
    elif any(s in mensaje_lower for s in ["logo", "marca", "branding", "identidad"]):
        return "branding"
    elif any(s in mensaje_lower for s in ["app", "aplicación", "aplicacion", "movil", "móvil"]):
        return "apps"
    elif any(s in mensaje_lower for s in ["marketing", "redes", "publicidad", "anuncios"]):
        return "marketing"
    elif any(s in mensaje_lower for s in ["automatizar", "proceso", "flujo", "optimizar"]):
        return "automatizacion"
    else:
        return None

def optimizar_instancia_eva(eva, mensaje_actual, session_id):
    """Optimiza la instancia de Eva para mejorar las respuestas"""
    
    # 1. Limitar el historial de conversación a lo esencial
    if len(eva.conversation_history) > 6:
        eva.conversation_history = eva.conversation_history[-6:]
    
    # 2. Ajustar configuración según el tipo de mensaje
    servicio = detectar_servicio_requerido(mensaje_actual)
    
    if "cotizar" in mensaje_actual.lower() or "precio" in mensaje_actual.lower() or "costo" in mensaje_actual.lower():
        # El usuario pregunta por precios, ajustar para incluir información comercial
        CONFIG["max_response_length"] = 350
        CONFIG["short_response_length"] = 250
        
        # Guardar el servicio detectado en la sesión para referencias futuras
        if session_id not in user_sessions:
            user_sessions[session_id] = {}
        user_sessions[session_id]["servicio_interes"] = servicio
        
    elif servicio:
        # El usuario menciona un servicio específico
        CONFIG["max_response_length"] = 300
        CONFIG["short_response_length"] = 200
        
        # Guardar el servicio detectado en la sesión para referencias futuras
        if session_id not in user_sessions:
            user_sessions[session_id] = {}
        user_sessions[session_id]["servicio_interes"] = servicio
        
    else:
        # Mensajes generales
        CONFIG["max_response_length"] = 250
        CONFIG["short_response_length"] = 150
    
    # 3. Forzar modo conciso para evitar truncamiento
    CONFIG["show_typing"] = False
    
    return eva

# Almacén simple para datos de usuario por sesión
user_sessions = {}

@app.route("/", methods=["GET"])
def home():
    return "EVA está corriendo en Render 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Falta el campo 'message' en el JSON."}), 400

        # Obtener mensaje limpio del usuario
        mensaje_original = data["message"]
        user_message = mensaje_original
        
        # Quitar prefijos que puedan causar confusión
        prefijos = ["Usuario:", "Asistente:", "Eva:"]
        for prefijo in prefijos:
            if user_message.startswith(prefijo):
                user_message = user_message[len(prefijo):].strip()
                
        session_id = data.get("sessionId", "default")
        
        # Crear instancia de Eva o recuperar la existente
        if session_id not in eva_instances:
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)
            
            # Inicializar nueva sesión
            user_sessions[session_id] = {"servicio_interes": None}
        
        eva = eva_instances[session_id]
        
        # Optimizar la instancia para mejorar las respuestas y evitar truncamiento
        eva = optimizar_instancia_eva(eva, user_message, session_id)
        
        # Modificar prompt si detectamos una solicitud de cotización
        servicio_interes = user_sessions[session_id].get("servicio_interes")
        if "cotizar" in user_message.lower() and servicio_interes and servicio_interes in PRECIOS_SERVICIOS:
            # Preprocesar la solicitud para incluir información de precios
            precio = PRECIOS_SERVICIOS[servicio_interes]
            informacion_precio = f"Nuestro servicio de {servicio_interes} tiene un precio {precio}."
            
            # Añadir esta información al mensaje
            user_message = f"{user_message}. [La ejecutiva sabe que: {informacion_precio}]"
        
        # Generar respuesta
        response = eva.get_response(user_message)
        
        # Verificar si la respuesta aborda la pregunta específica sobre cotización
        if "cotizar" in mensaje_original.lower() and servicio_interes:
            if PRECIOS_SERVICIOS[servicio_interes] not in response:
                # Si no se mencionó el precio, asegurarnos de incluirlo
                servicio_nombre = {
                    "web": "página web",
                    "ecommerce": "tienda online",
                    "branding": "identidad de marca",
                    "apps": "aplicación móvil",
                    "marketing": "marketing digital",
                    "automatizacion": "automatización de procesos"
                }.get(servicio_interes, servicio_interes)
                
                if "precio" not in response.lower() and "costo" not in response.lower():
                    precio_info = f" El precio para una {servicio_nombre} es {PRECIOS_SERVICIOS[servicio_interes]}."
                    
                    # Insertar en un buen lugar de la respuesta
                    punto_insercion = response.rfind('.')
                    if punto_insercion > len(response) // 2:
                        response = response[:punto_insercion] + precio_info + response[punto_insercion:]
                    else:
                        response += precio_info
        
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

        if session_id in eva_instances:
            del eva_instances[session_id]
        
        if session_id in user_sessions:
            del user_sessions[session_id]

        return jsonify({"status": "ok", "message": "Eva reiniciada correctamente"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)