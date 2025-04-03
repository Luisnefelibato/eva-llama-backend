from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Configuración
CONFIG = {
    "debug": True,
    "ollama_api_url": "https://huge-ads-smile.loca.lt/api/generate",
    "db_config": {
        "host": "dpg-cvllj3t6ubrc73f0ia50-a",
        "port": 5432,
        "dbname": "eva_db_27qk",
        "user": "eva_db_27qk_user",
        "password": "71GbjXoWwczOJ3frkcE8Iq4j6Yl5A5Vy"
    }
}

# Diccionario para mantener sesiones de usuarios (memoria)
user_sessions = {}

# Función para guardar en PostgreSQL
def guardar_en_postgres(rol, mensaje):
    try:
        conn = psycopg2.connect(**CONFIG["db_config"])
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO conversaciones (fecha, rol, mensaje)
            VALUES (%s, %s, %s)
        """, (datetime.now(), rol, mensaje))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] {e}")
        return False

def generar_respuesta(prompt, session_id="default"):
    """Genera una respuesta orientada a ventas para Antares Innovate"""
    try:
        # Recuperar nombre si existe en la sesión
        nombre = None
        if session_id in user_sessions and "nombre" in user_sessions[session_id]:
            nombre = user_sessions[session_id]["nombre"]
        
        # Buscar nombre en el prompt si no lo tenemos
        if not nombre:
            nombre_match = re.search(r'(?:me llamo|soy|mi nombre es)\s+([A-Za-zÁáÉéÍíÓóÚúÑñ]+(?:\s+[A-Za-zÁáÉéÍíÓóÚúÑñ]+)?)', prompt.lower())
            if nombre_match:
                nombre = nombre_match.group(1).strip().capitalize()
                # Guardar en sesión
                if session_id not in user_sessions:
                    user_sessions[session_id] = {}
                user_sessions[session_id]["nombre"] = nombre
        
        # Construir historial de chat si existe
        historial = ""
        if session_id in user_sessions and "mensajes" in user_sessions[session_id]:
            # Limitar a los últimos 3 intercambios
            mensajes = user_sessions[session_id]["mensajes"][-6:]
            for i in range(0, len(mensajes), 2):
                if i+1 < len(mensajes):
                    historial += f"Usuario: {mensajes[i]}\n"
                    historial += f"EVA: {mensajes[i+1]}\n"
        
        # Determinar el tema según palabras clave en el prompt
        palabras_clave = {
            "branding": ["marca", "branding", "logo", "diseño", "imagen", "identidad"],
            "diseño web": ["web", "página", "sitio", "landing", "ecommerce", "tienda online"],
            "desarrollo de apps": ["app", "aplicación", "móvil", "android", "ios", "celular"],
            "automatización": ["automatización", "proceso", "flujo", "robot", "rpa", "optimizar"],
            "marketing digital": ["marketing", "redes", "facebook", "instagram", "publicidad", "anuncios"]
        }
        
        tema_detectado = "general"
        for tema, palabras in palabras_clave.items():
            if any(palabra in prompt.lower() for palabra in palabras):
                tema_detectado = tema
                break
        
        # Prompt con instrucciones específicas según el tema detectado
        mensaje_con_contexto = f"""
        <INSTRUCCIONES>
        Eres EVA, ejecutiva de ventas de Antares Innovate, una agencia de transformación digital premium.
        NUNCA debes usar frases como "Me alegra que hayas decidido confiar en mí" o "Estoy aquí para escucharte".
        SIEMPRE menciónate como "Eva de Antares Innovate" y SIEMPRE ofrece servicios específicos.
        SIEMPRE habla de "nuestro equipo", "nuestros diseñadores", "nuestros desarrolladores".
        
        En cada respuesta DEBES:
        1. Mencionar Antares Innovate por lo menos una vez
        2. Ofrecer un servicio concreto relacionado con su necesidad
        3. Mencionar un beneficio específico de trabajar con nosotros
        4. Incitar a una reunión o próximo paso comercial
        
        Tus respuestas deben ser directas, personales y orientadas a VENTAS.
        Nuestros servicios: branding (desde $2,500 USD), web (desde $3,000 USD), apps ($8,000 USD), automatización ($5,000 USD).
        
        TEMA DETECTADO: {tema_detectado}
        </INSTRUCCIONES>
        
        <HISTORIAL>
        {historial}
        </HISTORIAL>

        Usuario: {prompt}
        EVA:
        """

        # Enviar solicitud a Ollama
        payload = {
            "model": "llama3",
            "prompt": mensaje_con_contexto,
            "stream": False,
            "max_tokens": 400
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.post(CONFIG["ollama_api_url"], json=payload, headers=headers)

        if response.status_code == 200:
            res_json = response.json()
            respuesta = res_json.get("response", "").strip()
            
            # Verificar si la respuesta no menciona Antares o es genérica
            respuesta_lower = respuesta.lower()
            frases_genericas = [
                "me alegra", "confiar en mí", "estoy aquí para", "como puedo ayudarte",
                "como asistente", "como ia", "como modelo"
            ]
            
            es_generica = any(frase in respuesta_lower for frase in frases_genericas)
            menciona_antares = "antares" in respuesta_lower
            
            # Si es genérica o no menciona Antares, usar respuesta fallback
            if es_generica or not menciona_antares:
                respuesta = generar_respuesta_fallback(tema_detectado, nombre)
            
            # Guardar en la sesión
            if session_id not in user_sessions:
                user_sessions[session_id] = {"mensajes": []}
            
            if "mensajes" not in user_sessions[session_id]:
                user_sessions[session_id]["mensajes"] = []
            
            user_sessions[session_id]["mensajes"].append(prompt)
            user_sessions[session_id]["mensajes"].append(respuesta)
            
            return respuesta
        else:
            return generar_respuesta_fallback("general", nombre)

    except Exception as e:
        print(f"[ERROR] al generar respuesta: {str(e)}")
        return generar_respuesta_fallback("general", nombre)

def generar_respuesta_fallback(tema="general", nombre=None):
    """Genera una respuesta de fallback orientada a ventas según el tema"""
    saludo = f"¡Hola {nombre}! " if nombre else "¡Hola! "
    
    respuestas = {
        "branding": (
            f"{saludo}Soy Eva de Antares Innovate. Nuestro equipo de diseño puede crear una identidad de marca "
            f"completa para tu negocio desde $2,500 USD, incluyendo logo, paleta de colores, tipografía y manual de marca. "
            f"Hemos ayudado a empresas a aumentar su reconocimiento de marca hasta en un 40%. "
            f"¿Te gustaría agendar una videollamada para analizar específicamente tu proyecto de branding?"
        ),
        "diseño web": (
            f"{saludo}Soy Eva de Antares Innovate. Nuestro equipo de desarrollo web puede crear un sitio profesional "
            f"y optimizado desde $3,000 USD. Incluimos diseño responsive, optimización SEO y panel de administración. "
            f"Nuestros clientes han incrementado sus conversiones en un 30% con nuestros diseños. "
            f"¿Prefieres que te muestre algunos ejemplos de nuestro portafolio o agendar directamente una reunión?"
        ),
        "desarrollo de apps": (
            f"{saludo}Soy Eva de Antares Innovate. Desarrollamos aplicaciones móviles personalizadas desde $8,000 USD "
            f"con interfaces intuitivas y funcionalidades adaptadas a tu negocio. Trabajamos con React Native para crear "
            f"aplicaciones multiplataforma de alto rendimiento. ¿Te gustaría que agendemos una llamada con nuestro líder "
            f"técnico para discutir tu idea de aplicación?"
        ),
        "automatización": (
            f"{saludo}Soy Eva de Antares Innovate. Nuestra especialidad en automatización de procesos ha ayudado a "
            f"empresas a reducir costos operativos hasta en un 40%. Implementamos soluciones desde $5,000 USD "
            f"según la complejidad de los procesos. ¿Qué procesos específicos te gustaría automatizar? "
            f"Podemos agendar una sesión diagnóstico sin costo para evaluar tu caso."
        ),
        "marketing digital": (
            f"{saludo}Soy Eva de Antares Innovate. Nuestras estrategias de marketing digital han generado hasta 3x de ROI "
            f"para nuestros clientes. Ofrecemos gestión de redes sociales, campañas de anuncios y posicionamiento SEO "
            f"desde $1,500 USD mensuales. ¿Te gustaría una evaluación gratuita de tu presencia digital actual?"
        ),
        "general": (
            f"{saludo}Soy Eva, ejecutiva de ventas de Antares Innovate. Ayudamos a empresas a crecer digitalmente "
            f"a través de servicios de branding, desarrollo web/apps y automatización de procesos. "
            f"Nuestros precios van desde $2,500 USD según el servicio y alcance del proyecto. "
            f"¿En qué área específica estás buscando apoyo para tu negocio? Con gusto podemos agendar una "
            f"videollamada para conocer más sobre tus necesidades."
        )
    }
    
    return respuestas.get(tema, respuestas["general"])

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
        
        # Generar respuesta
        response = generar_respuesta(user_message, session_id)

        # Guardar en PostgreSQL
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
    """Reinicia las sesiones"""
    try:
        data = request.get_json()
        session_id = data.get("sessionId", "default")
        
        if session_id in user_sessions:
            del user_sessions[session_id]
            return jsonify({"status": "success", "message": "Sesión reiniciada correctamente"})
        else:
            return jsonify({"status": "success", "message": "No existía sesión previa"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)