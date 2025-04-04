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

def extraer_info_usuario(mensaje):
    """Extrae información relevante del usuario del mensaje"""
    info = {}
    
    # Extraer nombre - evitar extraer "Eva" como nombre del cliente
    nombre_match = re.search(r'(?:me llamo|soy|mi nombre es) ([A-Za-záéíóúÁÉÍÓÚñÑ]+)', mensaje.lower())
    if nombre_match:
        nombre = nombre_match.group(1).strip().capitalize()
        # Verificar que no sea "Eva" para evitar confusiones
        if nombre.lower() != "eva":
            info['nombre'] = nombre
    
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
    elif any(s in mensaje.lower() for s in ["automatizar", "automatización", "proceso", "negocio"]):
        info['servicio'] = "automatizacion"
    elif any(s in mensaje.lower() for s in ["instagram", "redes", "social", "facebook"]):
        info['servicio'] = "marketing"
    
    return info

def limpiar_mensaje(mensaje):
    """Limpia el mensaje de prefijos innecesarios y estructura de conversación"""
    # Primero, eliminar prefijos comunes
    prefijos = ["Usuario:", "Asistente:", "Eva:"]
    mensaje_limpio = mensaje
    
    for prefijo in prefijos:
        if mensaje_limpio.startswith(prefijo):
            mensaje_limpio = mensaje_limpio[len(prefijo):].strip()
    
    # Buscar patrones de conversación (Eliminar las líneas anteriores)
    if "Usuario:" in mensaje_limpio or "Asistente:" in mensaje_limpio:
        # Obtener solo la última línea o consulta del usuario
        lineas = re.split(r'\nUsuario:|\nAsistente:|\nEva:', mensaje_limpio)
        if lineas:
            # Tomar la última línea relevante que no sea vacía
            for linea in reversed(lineas):
                if linea.strip():
                    mensaje_limpio = linea.strip()
                    break
    
    # Eliminar cualquier [CONTEXTO: ...] existente
    mensaje_limpio = re.sub(r'\[CONTEXTO:.*?\]', '', mensaje_limpio).strip()
    
    return mensaje_limpio

def crear_prompt_optimizado(mensaje, session_id):
    """Crea un prompt optimizado con instrucciones claras"""
    # Inicializar o actualizar sesión
    if session_id not in user_sessions:
        user_sessions[session_id] = {}
    
    # Actualizar información del usuario
    info_usuario = extraer_info_usuario(mensaje)
    user_sessions[session_id].update(info_usuario)
    
    # Preparar prompt con instrucciones específicas
    instrucciones = []
    
    # Añadir nombre si existe
    if user_sessions[session_id].get('nombre'):
        instrucciones.append(f"El cliente se llama {user_sessions[session_id]['nombre']}. Dirígete a él/ella por su nombre.")
    
    # Añadir servicio si existe
    if user_sessions[session_id].get('servicio'):
        servicio = user_sessions[session_id]['servicio']
        instrucciones.append(f"Está interesado en nuestro servicio de {servicio}.")
    
    # Añadir instrucciones generales
    instrucciones.append("Identifícate como Eva de Antares Innovate.")
    instrucciones.append("Mantén un tono profesional pero cercano.")
    
    # Crear prompt final
    if instrucciones:
        prompt_optimizado = f"{mensaje} [INSTRUCCIONES: {'. '.join(instrucciones)}]"
    else:
        prompt_optimizado = mensaje
    
    return prompt_optimizado

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
        
        # Crear instancia de Eva o recuperar la existente
        if session_id not in eva_instances:
            eva_instances[session_id] = EvaAssistant(typing_simulation=False)
        
        eva = eva_instances[session_id]
        
        # Optimizar historial para evitar sobrecarga de tokens
        if len(eva.conversation_history) > 6:
            eva.conversation_history = eva.conversation_history[-6:]
        
        # Crear prompt optimizado
        prompt_optimizado = crear_prompt_optimizado(user_message, session_id)
        
        # Modificar CONFIG para asegurar respuestas completas
        # Establecer límites más altos para no truncar las respuestas
        CONFIG["max_response_length"] = 1000
        CONFIG["short_response_length"] = 500
        
        # Generar respuesta
        response = eva.get_response(prompt_optimizado)
        
        # NO modificar la respuesta generada
        # Usamos la respuesta tal cual viene de Ollama
        
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