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

# Almacén simple para datos de usuario por sesión
user_sessions = {}

# Precios y detalles de servicios para referencias rápidas
SERVICIOS = {
    "web": {
        "nombre": "sitio web profesional",
        "precio": "desde $3,000 USD"
    },
    "landing": {
        "nombre": "landing page",
        "precio": "desde $1,800 USD"
    },
    "ecommerce": {
        "nombre": "tienda online",
        "precio": "desde $5,000 USD"
    },
    "branding": {
        "nombre": "identidad de marca",
        "precio": "desde $2,500 USD"
    },
    "app": {
        "nombre": "aplicación móvil",
        "precio": "desde $8,000 USD"
    },
    "automatizacion": {
        "nombre": "automatización de procesos",
        "precio": "desde $5,000 USD"
    }
}

def extraer_info_usuario(mensaje):
    """Extrae información relevante del usuario del mensaje"""
    info = {}
    
    # Extraer nombre
    nombre_match = re.search(r'(?:me llamo|soy|mi nombre es) ([A-Za-záéíóúÁÉÍÓÚñÑ]+)', mensaje.lower())
    if nombre_match:
        info['nombre'] = nombre_match.group(1).strip().capitalize()
    
    # Detectar servicio de interés
    if any(s in mensaje.lower() for s in ["landing page", "landing"]):
        info['servicio'] = "landing"
    elif any(s in mensaje.lower() for s in ["tienda", "ecommerce", "vender"]):
        info['servicio'] = "ecommerce"
    elif any(s in mensaje.lower() for s in ["web", "sitio", "página", "pagina"]):
        info['servicio'] = "web"
    elif any(s in mensaje.lower() for s in ["app", "aplicación", "aplicacion", "móvil"]):
        info['servicio'] = "app"
    elif any(s in mensaje.lower() for s in ["marca", "logo", "branding"]):
        info['servicio'] = "branding"
    elif any(s in mensaje.lower() for s in ["automatizar", "automatización", "proceso"]):
        info['servicio'] = "automatizacion"
    
    # Detectar negocio/producto
    negocio_match = re.search(r'(?:para|de|sobre) (?:mi|una|un) (?:negocio|empresa|tienda|sitio) (?:de|llamad[oa]|sobre) ([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)(?:\.|\,|\s|$)', mensaje.lower())
    if negocio_match:
        info['negocio'] = negocio_match.group(1).strip()
    
    # Detectar intenciones
    if any(s in mensaje.lower() for s in ["precio", "cuanto", "cuánto", "cotizar", "costo", "vale"]):
        info['intencion_precio'] = True
    
    return info

def construir_contexto(session_id, nuevo_mensaje):
    """Construye el contexto para enriquecer el mensaje enviado a Eva"""
    if session_id not in user_sessions:
        # Inicializar sesión
        user_sessions[session_id] = {}
    
    # Extraer nueva información del mensaje
    nueva_info = extraer_info_usuario(nuevo_mensaje)
    
    # Actualizar sesión con la nueva información
    for key, value in nueva_info.items():
        user_sessions[session_id][key] = value
    
    # Construir contexto para la respuesta
    datos_usuario = user_sessions[session_id]
    contexto = []
    
    # Añadir nombre si existe
    if 'nombre' in datos_usuario:
        contexto.append(f"El cliente se llama {datos_usuario['nombre']}.")
    
    # Añadir servicio si existe
    if 'servicio' in datos_usuario and datos_usuario['servicio'] in SERVICIOS:
        servicio = SERVICIOS[datos_usuario['servicio']]
        contexto.append(f"Está interesado en {servicio['nombre']} ({servicio['precio']}).")
    
    # Añadir negocio si existe
    if 'negocio' in datos_usuario:
        contexto.append(f"Su negocio es sobre {datos_usuario['negocio']}.")
    
    # Añadir otras intenciones relevantes
    if datos_usuario.get('intencion_precio', False):
        contexto.append("Está preguntando por precios.")
    
    # Devolver el contexto completo o una cadena vacía
    if contexto:
        return "[CONTEXTO: " + " ".join(contexto) + "]"
    return ""

def limpiar_mensaje(mensaje):
    """Limpia el mensaje de prefijos innecesarios"""
    prefijos = ["Usuario:", "Asistente:", "Eva:"]
    mensaje_limpio = mensaje
    
    for prefijo in prefijos:
        if mensaje_limpio.startswith(prefijo):
            mensaje_limpio = mensaje_limpio[len(prefijo):].strip()
    
    return mensaje_limpio

@app.route("/", methods=["GET"])
def home():
    return "EVA está corriendo en Render 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Falta el campo 'message' en el JSON."}), 400

        # Obtener y limpiar mensaje del usuario
        mensaje_original = data["message"]
        user_message = limpiar_mensaje(mensaje_original)
        
        session_id = data.get("sessionId", "default")
        
        # Construir contexto para el mensaje
        contexto = construir_contexto(session_id, user_message)
        
        # Preparar mensaje enriquecido con contexto
        mensaje_enriquecido = user_message
        if contexto:
            mensaje_enriquecido = f"{user_message} {contexto}"
        
        # Ajustar CONFIG según el tipo de mensaje
        if any(palabra in user_message.lower() for palabra in ["precio", "cotizar", "costo"]):
            CONFIG["max_response_length"] = 400  # Respuestas más largas para preguntas de precio
        else:
            CONFIG["max_response_length"] = 300  # Respuestas estándar para otras preguntas
        
        # Crear instancia de Eva o recuperar la existente
        if session_id not in eva_instances:
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)
        
        eva = eva_instances[session_id]
        
        # Optimizar historial para evitar sobrecarga de tokens
        if len(eva.conversation_history) > 6:
            eva.conversation_history = eva.conversation_history[-6:]
        
        # Generar respuesta con el mensaje enriquecido
        response = eva.get_response(mensaje_enriquecido)
        
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