#!/usr/bin/env python
"""
Eva con Llama3 - Asistente Virtual para Antares Innovate

Versión mejorada con funcionalidades ampliadas:
- Sistema de agendamiento de reuniones completo con Google Calendar
- Análisis de sentimiento para respuestas personalizadas
- Tono más cálido y personalizado
- Optimización de respuestas para evitar repeticiones
- Integración fluida con Google Meet

Autor: Antares Innovate
Versión: 4.0
"""

import sys
import os
import asyncio
import json
import random
import argparse
import time
import re
import requests
import time  # Añade esta línea si no existe
import pytz
import time
from datetime import datetime, time as timedelta, date, time as datetime_time
from typing import Dict, List, Optional, Any, Tuple, Union
import sqlite3

# Importar la base de conocimiento para fallback si es necesario
try:
    from prompts import CONTACT_INFO
except ImportError:
    CONTACT_INFO = [
        "\n\nPuedes contactarnos al +52 (55) 1234-5678.",
        "\n\nEscríbenos a contacto@antaresinnovate.com.",
        "\n\nVisita www.antaresinnovate.com para más información."
    ]

# Intentar importar integraciones de Google Calendar si están disponibles
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import base64
    
    GOOGLE_INTEGRATION_AVAILABLE = True
except ImportError:
    GOOGLE_INTEGRATION_AVAILABLE = False
    print("Bibliotecas de Google no disponibles. Funcionalidades de calendario desactivadas.")

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Configuraciones globales
CONFIG = {
    "min_response_time": 0.4,
    "max_response_time": 1.2,
    "char_typing_speed": 0.01,
    "show_typing": True,
    "thinking_messages": [
        "Analizando tu consulta...", 
        "Procesando información...", 
        "Buscando la mejor respuesta para ti...",
        "Preparando una respuesta personalizada...",
        "Consultando nuestra base de conocimiento..."
    ],
    "debug": True,
    "ollama_model": "llama3",
    "ollama_api_url": "https://huge-ads-smile.loca.lt/api/generate"
,
    "max_response_length": 800,  # Límite de caracteres para respuestas técnicas
    "short_response_length": 300,  # Límite para respuestas simples
    
    # Expresiones cálidas para variar el tono
    "warm_expressions": [
        "¡Me encanta poder ayudarte con esto!",
        "Estoy aquí para facilitarte las cosas",
        "Qué buena pregunta has hecho",
        "Me alegra que te intereses en nuestros servicios",
        "Cuenta conmigo para cualquier duda",
        "Será un placer ayudarte con eso",
        "¡Excelente elección!",
        "Trabajemos juntos en esto",
        "Estoy encantada de poder asistirte",
        "Confía en que haremos un gran trabajo juntos"
    ],
    
    # Nueva base de conocimiento estructurada en jerarquía informativa
    "knowledge_base_content": """
# IDENTIDAD DE MARCA
Antares Innovate es una agencia de transformación digital creativa. Combinamos creatividad, tecnología y consultoría para ayudar a empresas a escalar en el mundo digital. Operamos en Colombia y USA.

# PILARES PRINCIPALES
1. Creatividad: Branding, diseño y contenido que conecta con tu audiencia.
2. Tecnología: Soluciones digitales a medida, desde web hasta apps y chatbots.
3. Consultoría: Acompañamiento en transformación digital y automatización.

# CREATIVIDAD - SERVICIOS
• Identidad visual (logos, colores, tipografías)
• Manuales de marca y Brandbooks
• Storytelling visual
• Producción de video y postproducción
• Motion graphics y animación 2D/3D
• Ilustraciones, concept art y vectores
• Generación de contenido con IA
• Comerciales y audiovisuales de alto impacto

# TECNOLOGÍA - SERVICIOS
• Diseño UI/UX premiado (Figma, prototipado, pruebas)
• Desarrollo web (React, Next.js, Tailwind, WordPress)
• Apps web y móviles
• Integración con APIs y sistemas externos
• Chatbots inteligentes (con audio y voz)
• Modelado y render 3D para web

# CONSULTORÍA - SERVICIOS
• Automatización de procesos empresariales (BPA)
• Automatización robótica (RPA)
• Integración de sistemas
• Desarrollo de flujos de trabajo
• Chatbots y asistentes virtuales
• Gestión empresarial y digitalización
• Modelos de negocio digitales
• Consultoría en innovación y escalamiento

# DETALLES TÉCNICOS - AUTOMATIZACIÓN
• BPA: Transformamos operaciones completas, desde entrada de datos hasta informes.
• RPA: Robots de software que realizan tareas repetitivas a alta velocidad.
• Integración: Conectamos aplicaciones eliminando silos de información.
• Flujos de Trabajo: Secuencias optimizadas con aprobaciones automáticas.
• Beneficios: 40% reducción de costos operativos, eliminación de errores.

# DETALLES TÉCNICOS - DISEÑO Y DESARROLLO
• UI/UX: Diseño centrado en usuario, wireframes, prototipos interactivos
• Desarrollo: React, Next.js, Tailwind, Node.js, Laravel, WordPress
• Apps: React Native, PWA, integración con APIs
• Chatbots: NLP, integración WhatsApp, voz, IA generativa
• 3D: Three.js, modelado, animación, visualización
# SIMULACIONES DE CONVERSACIÓN

# SIMULACIÓN 1 - Desarrollo de E-commerce para Tienda de Ropa
Usuario: "¡Hola! Hablo con alguien de ANTARES, necesito ayuda con una página web para mi tienda de ropa."
EVA: "¡Hola! Soy EVA, encantada. Claro que podemos ayudarle. Cuénteme, ¿ya tiene algún sitio web o empezarían desde cero?"
Usuario: "Desde cero, no sé nada de tecnología."
EVA: "No hay problema, nosotros lo guiamos. ¿Qué funcionalidades le gustaría tener? Por ejemplo: catálogo, carrito de compras…"
Usuario: "Sí, eso, y que sea fácil de usar."
EVA: "Perfecto. ¿Tiene fotos profesionales de sus productos?"
Usuario: "No, solo las tomo yo."
EVA: "Podemos incluir un paquete de fotografía. ¿Cuántos productos quiere mostrar?"
Usuario: "Unos 50."
EVA: "Entiendo. Para darle una solución exacta, ¿le parece si coordinamos una reunión con nuestro equipo de desarrollo? Así definimos plazos y costos."
Usuario: "Sí, ¿cuándo están disponibles?"
EVA: "Mañana a las 3 PM. ¿Le envío el link de Zoom?"

# SIMULACIÓN 2 - Campaña de Redes Sociales para Restaurante
Usuario: "Hola, ¿es ANTARES? Quiero promocionar mi restaurante en redes sociales."
EVA: "¡Hola! Soy EVA, claro que sí. ¿Actualmente maneja sus redes o las tiene inactivas?"
Usuario: "Las tengo, pero no generan ventas."
EVA: "Entiendo. ¿Qué tipo de contenido publica? ¿Fotos, videos, promociones?"
Usuario: "Solo fotos del menú."
EVA: "Podríamos crear videos cortos y anuncios segmentados. ¿Tiene un presupuesto mensual para publicidad?"
Usuario: "Unos $500 USD."
EVA: "Excelente. Con eso podemos lograr buen alcance. ¿Quiere incluir influencers locales?"
Usuario: "No lo había pensado… ¿Funciona?"
EVA: "Sí, aumenta la confianza. Le enviaré casos de éxito. Para personalizar su estrategia, ¿le parece una reunión con nuestro experto en marketing digital?"
Usuario: "¡Sí!"
EVA: "¿Disponible el jueves a las 11 AM?"

# SIMULACIÓN 3 - Sistema de Reservas para Hotel Boutique
Usuario: "Buen día, ¿hablo con ANTARES? Necesito un sistema para reservas en línea."
EVA: "¡Buen día! Soy EVA, claro que podemos ayudarle. ¿Actualmente cómo reciben reservas?"
Usuario: "Por WhatsApp y llamadas… es un caos."
EVA: "Entiendo. Nuestro sistema integra calendario, pagos y confirmación automática. ¿Tiene sitio web?"
Usuario: "Sí, pero muy básico."
EVA: "Podemos vincularlo. ¿Qué métodos de pago quiere aceptar?"
Usuario: "Tarjetas y PayPal."
EVA: "Perfecto. ¿Cuántas habitaciones tiene?"
Usuario: "10."
EVA: "Para asegurar que el sistema se adapte a sus necesidades, ¿le parece si habla directamente con nuestro líder de desarrollo? Él le explicará los detalles técnicos."
Usuario: "¡Sí, por favor!"
EVA: "¿Disponible el viernes a las 9 AM?"

# SIMULACIÓN 4 - Desarrollo de E-commerce para Artesanías
Usuario: "Hola, ¿es ANTARES? Quiero vender mis artesanías en línea."
EVA: "¡Hola! Soy EVA. Claro que podemos ayudarle. ¿Ya tiene algún sitio web o empezaría desde cero?"
Usuario: "Desde cero, no sé nada de tecnología."
EVA: "No hay problema. ¿Qué funcionalidades le gustaría? Por ejemplo: catálogo, carrito de compras, pasarela de pagos..."
Usuario: "Todo eso, y que sea fácil de manejar."
EVA: "Perfecto. ¿Tiene fotos profesionales de sus productos?"
Usuario: "No, solo las tomo con mi celular."
EVA: "Podemos incluir un paquete de fotografía. ¿Cuántos productos quiere mostrar inicialmente?"
Usuario: "Unos 30."
EVA: "Entendido. Para ajustar detalles, ¿le parece una reunión con nuestro equipo de desarrollo? Podemos hacerlo mañana a las 10 AM."

# SIMULACIÓN 5 - App Móvil para Gimnasio
Usuario: "¿Hacen apps para reservar clases de gimnasio?"
EVA: "¡Hola! Soy EVA. Sí, desarrollamos apps personalizadas. Actualmente, ¿cómo manejan las reservas?"
Usuario: "Por WhatsApp y es un desorden."
EVA: "Entiendo. Nuestra app incluiría perfil de usuario, calendario y notificaciones. ¿Quiere integrar pagos en línea?"
Usuario: "Sí, pero que sea seguro."
EVA: "Usamos Stripe y PayPal. ¿Tiene preferencia de plataforma: iOS, Android o ambas?"
Usuario: "Ambas, pero con bajo costo."
EVA: "Trabajamos con tecnología híbrida para reducir costos. ¿Cuántos usuarios activos tiene?"
Usuario: "Unos 150."
EVA: "Perfecto. ¿Le gustaría una demo de una app similar? Puedo coordinarla para el jueves."

# SIMULACIÓN 6 - Ciberseguridad para Clínica Médica
Usuario: "¡Urgente! Necesito proteger los datos de mis pacientes."
EVA: "Soy EVA. Tranquilo, hemos trabajado con HIPAA. ¿Han tenido intentos de hackeo?"
Usuario: "Sí, y nos preocupa el ransomware."
EVA: "Implementaremos firewall, encriptación y capacitación anti-phishing. ¿Cuántos empleados acceden al sistema?"
Usuario: "50, entre médicos y administrativos."
EVA: "¿Almacenan imágenes médicas (Rayos X, etc.)?"
Usuario: "Sí, en servidores locales."
EVA: "Migraremos todo a la nube con backups automáticos. ¿Tienen un presupuesto asignado?"
Usuario: "Sí, pero quiero una auditoría primero."
EVA: "Perfecto. Nuestro experto en salud puede visitarlos mañana. ¿A qué hora?"

# SIMULACIÓN 7 - Marketing Digital para Restaurante
Usuario: "¿Hacen publicidad para restaurantes?"
EVA: "¡Hola! Soy EVA. Sí, nos especializamos en gastronomía. ¿Qué redes sociales usa actualmente?"
Usuario: "Instagram, pero no genero ventas."
EVA: "¿Publica stories con promociones o solo fotos del menú?"
Usuario: "Solo fotos... no tengo tiempo."
EVA: "Crearemos contenido diario y anuncios segmentados. ¿A qué público quiere llegar?"
Usuario: "Familias y jóvenes adultos."
EVA: "¿Tiene un presupuesto mensual para publicidad?"
Usuario: "Unos $500 USD."
EVA: "Con eso lograremos buen alcance. ¿Comenzamos el lunes con una estrategia inicial?"


# INFORMACIÓN COMERCIAL
• Automatización: Proyectos desde $5,000 USD según alcance
• Diseño web: Desde $3,000 USD con CMS incluido
• Apps: Desde $8,000 USD por plataforma
• Chatbots: Desde $3,000 USD con integraciones básicas
• Consultoría: $150 USD/hora o proyectos desde $10,000 USD

# CONTACTO
Tel: +52 (689) 331 2690
Email: contacto@antaresinnovate.com
Web: www.antaresinnovate.com
    """,
    
    "google_credentials_file": "credentials.json",
    "google_token_file": "token.json",
    "google_scopes": [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/gmail.send"
    ],
    "company_email": "contacto@antaresinnovate.com",
    "calendar_id": "primary",
    
    # Nuevo: timezone para reuniones
    "timezone": "America/Mexico_City",
    
    # Nuevo: plantillas de correo para reuniones
    "email_templates": {
        "meeting_confirmation": {
            "subject": "¡Reunión confirmada con Antares Innovate!",
            "body_html": """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .header { background-color: #003366; padding: 20px; text-align: center; color: white; }
                    .content { padding: 20px; background-color: #ffffff; }
                    .footer { background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; }
                    .button { display: inline-block; background-color: #FF6600; color: white; text-decoration: none; padding: 10px 20px; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Reunión Confirmada</h1>
                    </div>
                    <div class="content">
                        <h2>¡Hola {{nombre}}!</h2>
                        
                        <p>Tu reunión con Antares Innovate ha sido confirmada para:</p>
                        
                        <p><strong>Fecha:</strong> {{fecha}}<br>
                        <strong>Hora:</strong> {{hora}} ({{timezone}})<br>
                        <strong>Duración:</strong> {{duracion}} minutos</p>
                        
                        <p>Podrás unirte a través del siguiente enlace de Google Meet:</p>
                        
                        <p style="text-align: center;">
                            <a href="{{meet_link}}" class="button">Unirse a la reunión</a>
                        </p>
                        
                        <p>Si no puedes asistir, por favor contáctanos con anticipación para reprogramar.</p>
                        
                        <p>¡Esperamos verte pronto!</p>
                        
                        <p>El equipo de Antares Innovate</p>
                    </div>
                    <div class="footer">
                        <p>Antares Innovate | contacto@antaresinnovate.com | +52 (55) 1234-5678</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
    }
}

# Utilidades para simular escritura humana
def simulate_thinking(message_length=None):
    """Simula tiempo de pensamiento antes de responder"""
    base_time = random.uniform(CONFIG["min_response_time"], CONFIG["max_response_time"])
    if message_length:
        complexity_factor = min(message_length / 100, 2.0)
        thinking_time = base_time * (1.0 + (complexity_factor * 0.5))
    else:
        thinking_time = base_time
    if CONFIG["show_typing"]:
        thinking_message = random.choice(CONFIG["thinking_messages"])
        print(f"\n{Colors.YELLOW}[{thinking_message}]{Colors.ENDC}", end="", flush=True)
        steps = int(thinking_time / 0.3)
        for _ in range(steps):
            print(".", end="", flush=True)
            time.sleep(0.3)
        print("\r" + " " * (len(thinking_message) + 15), end="\r", flush=True)
    else:
        time.sleep(thinking_time)

def simulate_typing(text, speed_variation=0.3):
    """Simula escritura humana con velocidad variable"""
    if not CONFIG["show_typing"]:
        print(f"\n{Colors.GREEN}Eva:{Colors.ENDC} {text}")
        return
    
    print(f"\n{Colors.GREEN}Eva:{Colors.ENDC} ", end="", flush=True)
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= random.randint(2, 6) or word[-1] in ['.', '!', '?']:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    for i, chunk in enumerate(chunks):
        if i > 0:
            time.sleep(random.uniform(0.15, 0.5))
        for char in chunk:
            char_speed = CONFIG["char_typing_speed"] * (1 + random.uniform(-speed_variation, speed_variation))
            if char in ['.', ',', '!', '?', ':', ';']:
                char_speed *= 2
            print(char, end="", flush=True)
            time.sleep(char_speed)
        if i < len(chunks) - 1:
            print(" ", end="", flush=True)

class DatabaseManager:
    """Gestor de base de datos para almacenar conversaciones."""
    
    def __init__(self, db_path="conversaciones_eva.db"):
        """Inicializa la conexión a la base de datos."""
        self.db_path = db_path
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Inicializa la estructura de la base de datos."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Crear tabla para usuarios
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                email TEXT,
                telefono TEXT,
                empresa TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Crear tabla para conversaciones
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                iniciada_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            ''')
            
            # Crear tabla para mensajes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversacion_id INTEGER,
                rol TEXT,
                contenido TEXT,
                intencion TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversacion_id) REFERENCES conversaciones (id)
            )
            ''')
            
            # Nueva tabla para reuniones
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS reuniones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                event_id TEXT,
                fecha TEXT,
                hora TEXT,
                meet_link TEXT,
                estado TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            ''')
            
            self.conn.commit()
            if CONFIG["debug"]:
                print(f"Base de datos inicializada en {self.db_path}")
            
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
    
    def save_user(self, user_info):
        """Guarda o actualiza información del usuario."""
        try:
            cursor = self.conn.cursor()
            
            # Verificar si el usuario ya existe (por email o teléfono)
            user_id = None
            if user_info.get("email"):
                cursor.execute("SELECT id FROM usuarios WHERE email = ?", (user_info["email"],))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id and user_info.get("telefono"):
                cursor.execute("SELECT id FROM usuarios WHERE telefono = ?", (user_info["telefono"],))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
            
            # Actualizar usuario existente o insertar nuevo
            if user_id:
                # Actualizar datos que no sean None
                updates = []
                params = []
                for key, value in user_info.items():
                    if value and key in ["nombre", "email", "telefono", "empresa"]:
                        updates.append(f"{key} = ?")
                        params.append(value)
                
                if updates:
                    params.append(user_id)
                    cursor.execute(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?", params)
            else:
                # Insertar nuevo usuario
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, telefono, empresa) VALUES (?, ?, ?, ?)",
                    (
                        user_info.get("nombre"),
                        user_info.get("email"),
                        user_info.get("telefono"),
                        user_info.get("empresa")
                    )
                )
                user_id = cursor.lastrowid
            
            self.conn.commit()
            return user_id
            
        except sqlite3.Error as e:
            print(f"Error al guardar usuario: {e}")
            return None
    
    def start_conversation(self, user_id=None):
        """Inicia una nueva conversación."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO conversaciones (usuario_id) VALUES (?)", (user_id,))
            conversation_id = cursor.lastrowid
            self.conn.commit()
            return conversation_id
        except sqlite3.Error as e:
            print(f"Error al iniciar conversación: {e}")
            return None
    
    def save_message(self, conversation_id, message):
        """Guarda un mensaje en la base de datos."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO mensajes (conversacion_id, rol, contenido, intencion, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    conversation_id,
                    message.get("rol"),
                    message.get("contenido"),
                    message.get("intencion", ""),
                    message.get("timestamp", datetime.now().isoformat())
                )
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error al guardar mensaje: {e}")
            return None
    
    def save_meeting(self, user_id, event_data):
        """Guarda información de una reunión agendada."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO reuniones 
                   (usuario_id, event_id, fecha, hora, meet_link, estado) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    event_data.get("id", ""),
                    event_data.get("fecha", ""),
                    event_data.get("hora", ""),
                    event_data.get("meet_link", ""),
                    "confirmada"
                )
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error al guardar reunión: {e}")
            return None
    
    def save_conversation(self, user_info, messages):
        """Guarda una conversación completa con sus mensajes."""
        try:
            # Guardar o actualizar usuario
            user_id = self.save_user(user_info)
            
            # Iniciar conversación
            conversation_id = self.start_conversation(user_id)
            
            # Guardar mensajes
            for message in messages:
                self.save_message(conversation_id, message)
            
            return conversation_id
        except Exception as e:
            print(f"Error al guardar conversación: {e}")
            return None

class GoogleCalendarIntegration:
    """Clase para manejar integraciones con Google Calendar."""
    
    def __init__(self):
        """Inicializa la integración con Google Calendar."""
        self.creds = None
        self.calendar_service = None
        self.gmail_service = None
        
        if not GOOGLE_INTEGRATION_AVAILABLE:
            if CONFIG["debug"]:
                print("Bibliotecas de Google no disponibles. Funcionalidades de calendario desactivadas.")
            return
            
        # Intentar cargar credenciales
        self._load_credentials()
    
    def _load_credentials(self):
        """Carga o solicita credenciales para API de Google."""
        # Verificar si existen archivos de credenciales
        if not os.path.exists(CONFIG["google_credentials_file"]):
            if CONFIG["debug"]:
                print(f"Archivo de credenciales {CONFIG['google_credentials_file']} no encontrado.")
            return
            
        # Cargar credenciales existentes
        if os.path.exists(CONFIG["google_token_file"]):
            with open(CONFIG["google_token_file"], 'r') as token:
                self.creds = Credentials.from_authorized_user_info(
                    json.load(token), CONFIG["google_scopes"])
                
        # Verificar si las credenciales son válidas
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    if CONFIG["debug"]:
                        print(f"Error al refrescar credenciales: {e}")
                    self._request_new_credentials()
            else:
                self._request_new_credentials()
                
            # Guardar las credenciales para la próxima ejecución
            if self.creds:
                with open(CONFIG["google_token_file"], 'w') as token:
                    token.write(self.creds.to_json())
    
    def _request_new_credentials(self):
        """Solicita nuevas credenciales mediante OAuth."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CONFIG["google_credentials_file"], CONFIG["google_scopes"])
            self.creds = flow.run_local_server(port=0)
            if CONFIG["debug"]:
                print("Nuevas credenciales obtenidas correctamente.")
        except Exception as e:
            if CONFIG["debug"]:
                print(f"Error al obtener nuevas credenciales: {e}")
    
    def init_services(self):
        """Inicializa los servicios de Google Calendar y Gmail."""
        if not self.creds:
            if CONFIG["debug"]:
                print("No hay credenciales disponibles. No se pueden inicializar servicios.")
            return False
            
        try:
            # Inicializar servicio de calendario
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
            
            # Inicializar servicio de Gmail
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
            
            return True
        except Exception as e:
            if CONFIG["debug"]:
                print(f"Error al inicializar servicios de Google: {e}")
            return False
    
    def get_available_slots(self, 
                           start_date: date, 
                           end_date: date = None, 
                           working_hours: Tuple[int, int] = (9, 18),
                           duration_minutes: int = 60) -> List[Dict]:
        """
        Obtiene slots disponibles en el calendario.
        
        Args:
            start_date: Fecha de inicio para buscar
            end_date: Fecha de fin (por defecto, 5 días después de start_date)
            working_hours: Horario laboral como (hora_inicio, hora_fin)
            duration_minutes: Duración de la reunión en minutos
            
        Returns:
            Lista de slots disponibles como {"fecha": date, "hora": time, "datetime": datetime}
        """
        if not self.calendar_service:
            if not self.init_services():
                return []
        
        # Si no se especifica end_date, usar 5 días laborables después de start_date
        if not end_date:
            end_date = start_date
            days_to_add = 0
            business_days = 0
            
            while business_days < 5:
                days_to_add += 1
                next_day = start_date + timedelta(days=days_to_add)
                if next_day.weekday() < 5:  # 0-4 es lunes a viernes
                    business_days += 1
                    end_date = next_day
        
        # Convertir fechas a datetime con timezone
        tz = pytz.timezone(CONFIG["timezone"])
        start_dt = datetime.combine(start_date, datetime_time(0, 0)).replace(tzinfo=tz)
        end_dt = datetime.combine(end_date, datetime_time(23, 59)).replace(tzinfo=tz)
        
        try:
            # Obtener eventos en el rango de fechas
            events_result = self.calendar_service.events().list(
                calendarId=CONFIG["calendar_id"],
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Generar todos los slots posibles en días laborables
            available_slots = []
            current_date = start_date
            
            while current_date <= end_date:
                # Omitir fines de semana
                if current_date.weekday() < 5:  # 0-4 es lunes a viernes
                    # Generar slots para cada hora laboral
                    for hour in range(working_hours[0], working_hours[1]):
                        for minute in [0, 30]:  # Slots cada 30 minutos
                            slot_time = datetime_time(hour, minute)
                            slot_dt = datetime.combine(current_date, slot_time)
                            
                            # Verificar que el slot no esté en el pasado
                            now = datetime.now()
                            if slot_dt <= now:
                                continue
                                
                            # Verificar que no haya solapamiento con eventos existentes
                            slot_end_dt = slot_dt + timedelta(minutes=duration_minutes)
                            is_available = True
                            
                            for event in events:
                                # Extraer tiempos de inicio y fin del evento
                                event_start_str = event['start'].get('dateTime')
                                event_end_str = event['end'].get('dateTime')
                                
                                if event_start_str and event_end_str:
                                    event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                                    event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
                                    
                                    # Convertir a zona horaria local
                                    event_start = event_start.astimezone(tz)
                                    event_end = event_end.astimezone(tz)
                                    
                                    # Verificar solapamiento
                                    if (slot_dt < event_end and slot_end_dt > event_start):
                                        is_available = False
                                        break
                            
                            if is_available:
                                slot_info = {
                                    "fecha": current_date,
                                    "hora": slot_time,
                                    "datetime": slot_dt
                                }
                                available_slots.append(slot_info)
                
                current_date += timedelta(days=1)
            
            return available_slots
            
        except Exception as e:
            if CONFIG["debug"]:
                print(f"Error al obtener slots disponibles: {e}")
            return []
    
    def create_calendar_event(self, 
                              summary: str, 
                              start_time: datetime,
                              end_time: datetime,
                              attendees: list,
                              description: str = "",
                              location: str = "",
                              timezone: str = "America/Mexico_City",
                              add_video_conference: bool = True) -> dict:
        """
        Crea un evento en Google Calendar y envía invitaciones por correo.
        
        Args:
            summary: Título del evento
            start_time: Fecha y hora de inicio
            end_time: Fecha y hora de fin
            attendees: Lista de correos electrónicos de participantes
            description: Descripción del evento
            location: Ubicación del evento
            timezone: Zona horaria
            add_video_conference: Si se debe añadir un enlace de Google Meet
            
        Returns:
            Información del evento creado o diccionario vacío en caso de error
        """
        if not self.calendar_service:
            if not self.init_services():
                return {}
        
        # Formatear correos de asistentes
        formatted_attendees = [{'email': email} for email in attendees]
        
        # Crear evento
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': timezone,
            },
            'attendees': formatted_attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30}
                ]
            },
        }
        
        # Añadir datos de conferencia (Google Meet)
        if add_video_conference:
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f'meeting-{int(time.datetime_time())}',  # ID único
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        
        try:
            created_event = self.calendar_service.events().insert(
                calendarId=CONFIG["calendar_id"],
                body=event,
                conferenceDataVersion=1 if add_video_conference else 0,  # Necesario para Meet
                sendUpdates='all'  # Enviar invitaciones por correo
            ).execute()
            
            if CONFIG["debug"]:
                print(f"Evento creado: {created_event.get('htmlLink')}")
            return created_event
        except Exception as e:
            if CONFIG["debug"]:
                print(f"Error al crear evento: {e}")
            return {}
    
    def send_email(self, 
                  to: str, 
                  subject: str, 
                  body_html: str,
                  cc: list = None) -> bool:
        """
        Envía un correo electrónico HTML usando Gmail API.
        
        Args:
            to: Correo del destinatario
            subject: Asunto del correo
            body_html: Cuerpo del correo en formato HTML
            cc: Lista de correos en copia
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.gmail_service:
            if not self.init_services():
                return False
        
        try:
            # Crear mensaje multipart
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ','.join(cc)
                
            # Adjuntar versión HTML
            html_part = MIMEText(body_html, 'html')
            message.attach(html_part)
            
            # Codificar mensaje para Gmail API
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Enviar mensaje
            send_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': encoded_message}
            ).execute()
            
            if CONFIG["debug"]:
                print(f"Correo enviado con ID: {send_message['id']}")
            return True
        except Exception as e:
            if CONFIG["debug"]:
                print(f"Error al enviar correo: {e}")
            return False
    
    def send_meeting_confirmation_email(self, 
                                       recipient_email: str, 
                                       recipient_name: str, 
                                       meeting_info: Dict) -> bool:
        """
        Envía un correo de confirmación de reunión con formato atractivo.
        
        Args:
            recipient_email: Correo del destinatario
            recipient_name: Nombre del destinatario
            meeting_info: Diccionario con información de la reunión (fecha, hora, meet_link)
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.gmail_service:
            if not self.init_services():
                return False
                
        try:
            # Preparar plantilla de correo
            template = CONFIG["email_templates"]["meeting_confirmation"]["body_html"]
            subject = CONFIG["email_templates"]["meeting_confirmation"]["subject"]
            
            # Reemplazar variables en la plantilla
            email_body = template.replace("{{nombre}}", recipient_name or "Estimado/a cliente")
            email_body = email_body.replace("{{fecha}}", meeting_info.get("fecha_str", ""))
            email_body = email_body.replace("{{hora}}", meeting_info.get("hora_str", ""))
            email_body = email_body.replace("{{timezone}}", CONFIG["timezone"])
            email_body = email_body.replace("{{duracion}}", str(meeting_info.get("duracion", 60)))
            email_body = email_body.replace("{{meet_link}}", meeting_info.get("meet_link", "#"))
            
            # Enviar correo
            return self.send_email(recipient_email, subject, email_body)
        except Exception as e:
            if CONFIG["debug"]:
                print(f"Error al enviar correo de confirmación: {e}")
            return False

class OllamaClient:
    """Cliente para comunicarse con la API de Ollama."""
    
    def __init__(self, model_name="llama3", api_url="https://eva-llama-backend.onrender.com/api/generate"):
        """
        Inicializa el cliente de Ollama.
        
        Args:
            model_name: llama3
            api_url:"https://eva-llama-backend.onrender.com/api/generate"
        """
        self.model_name = model_name
        self.api_url = "https://eva-llama-backend.onrender.com/api/generate"

        self.check_connection()
    
    def check_connection(self) -> bool:
        """
        Verifica que Ollama esté disponible.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Hacemos una solicitud a la API de Ollama para verificar la conexión
            response = requests.get(self.api_url.replace('/generate', '/tags'))
            
            if response.status_code == 200:
                if CONFIG["debug"]:
                    available_models = [model.get("name", "") for model in response.json().get("models", [])]
                    print(f"Modelos disponibles en Ollama: {', '.join(available_models)}")
                return True
            else:
                if CONFIG["debug"]:
                    print(f"Error al conectar con Ollama: Código {response.status_code}")
                return False
        except Exception as e:
            if CONFIG["debug"]:
                print(f"Error al intentar conectar con Ollama: {str(e)}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 800) -> str:
        try:
            payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "max_tokens": max_tokens
        }

            if CONFIG["debug"]:
                print(f"[DEBUG] Enviando solicitud a Ollama → {self.api_url}")
            print(f"[DEBUG] Payload: {payload}")

            headers = {
     "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"  # Simula navegador para evitar 403
}
            response = requests.post(self.api_url, json=payload, headers=headers)


            if response.status_code == 200:
                res_json = response.json()
                full_response = res_json.get("response", "").strip()

                if CONFIG["debug"]:
                    print(f"[DEBUG] Respuesta de Ollama: {full_response}")

                return full_response  # ✅ Esto debe ir FUERA del if debug

            else:
                if CONFIG["debug"]:
                    print(f"[ERROR] Ollama devolvió código: {response.status_code}")
                print(response.text)
                return ""  # Si no fue 200, devolvemos vacío

        except Exception as e:
            if CONFIG["debug"]:
                print(f"[ERROR] al generar respuesta con Ollama: {str(e)}")
            return ""


class SentimentAnalyzer:
    """Analizador de sentimiento para personalizar respuestas según el tono del usuario."""
    
    def analyze(self, message: str) -> Dict:
        """
        Analiza el sentimiento de un mensaje.
        
        Args:
            message: Mensaje a analizar
            
        Returns:
            Diccionario con información de sentimiento
        """
        message_lower = message.lower()
        
        # Palabras positivas
        positive_words = [
    "gracias", "excelente", "genial", "bueno", "increíble", "perfecto", "fantástico",
    "maravilloso", "encantado", "feliz", "contento", "alegre", "satisfecho",
    "me encanta", "muy bien", "todo claro", "qué bien", "buen trabajo", "me gusta", "¡super!"
]

        
        # Palabras negativas
        negative_words = [
    "malo", "terrible", "pésimo", "horrible", "frustrante", "molesto", "enojado",
    "inútil", "confuso", "difícil", "problema", "error", "fallo", "no funciona",
    "mal servicio", "no entiendo", "demasiado complicado", "no me sirve", "desesperante",
    "decepcionado", "no me gusta"
]

        
        # Palabras urgentes
        urgency_words = [
    "urgente", "rápido", "pronto", "ahora", "inmediatamente", "ya", "lo antes posible",
    "emergencia", "crítico", "prioritario", "plazo", "fecha límite", "lo necesito hoy",
    "apúrate", "sin demora", "es para ya", "de inmediato"
]

        
        # Contar ocurrencias
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        urgency_count = sum(1 for word in urgency_words if word in message_lower)
        
        # Analizar longitud y signos de puntuación
        words = message.split()
        word_count = len(words)
        exclamation_count = message.count('!')
        question_count = message.count('?')
        
        # Determinar sentimiento general
        sentiment = "positive"
        if positive_count > negative_count and positive_count > 0:
            sentiment = "positive"
        elif negative_count > positive_count and negative_count > 0:
            sentiment = "negative"
        
        # Determinar nivel de urgencia
        urgency = "normal"
        if urgency_count > 0 or exclamation_count > 2:
            urgency = "high"
        
        # Determinar nivel de interés
        interest = "medium"
        if word_count > 30 or question_count > 2:
            interest = "high"
        elif word_count < 5 and question_count == 0:
            interest = "low"
        
        return {
            "sentiment": sentiment,
            "urgency": urgency,
            "interest": interest,
            "word_count": word_count,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "questions": question_count,
            "exclamations": exclamation_count
        }

class EvaAssistant:
    """Asistente virtual Eva para Antares Innovate usando Llama3 vía Ollama."""
    
    def __init__(self, typing_simulation: bool = True):
        """Inicializa el asistente virtual."""
        if CONFIG["debug"]:
            print(f"{Colors.YELLOW}[Inicialización] Iniciando Eva con Llama3...{Colors.ENDC}")
        
        self.typing_simulation = typing_simulation
        
        self.conversation_history = []
        self.message_counter = 0
        self.db_manager = DatabaseManager()
        self.conversation_db_id = None
        
        self.user_info = {
    "nombre": None,
    "is_returning_user": False,
    "intereses": [],                  # Lista dinámica basada en intenciones detectadas
    "empresa": None,
    "email": None,
    "telefono": None,
    "sector": None,
    "pilar_interes": [],              # Nuevo: Puede haber más de un pilar detectado
    "nivel_tecnico": "alto",         # Puede ser: "bajo", "medio", "alto", "experto"
    "sentimiento": "positive",         # Puede ser: "positivo", "neutral", "negativo"
    "fase_conversacion": "inicio",    # Nuevo: estado global del flujo (inicio, diagnóstico, propuesta, cierre)

    # Seguimiento del proceso de agendamiento de reunión
    "reunion_state": {
        "solicitando_email": False,
        "solicitando_fecha": False,
        "solicitando_hora": False,
        "fecha_propuesta": None,
        "hora_propuesta": None,
        "reunion_confirmada": False,  # Nuevo: confirma si ya fue agendada
        "canal": None                 # Nuevo: Zoom, Meet, WhatsApp, etc.
    },

    # Nuevo: historial conversacional corto para contexto inmediato
    "ultimos_mensajes": [],          # Últimos 5 mensajes clave del usuario
    "intencion_actual": None,        # Última intención detectada (ej: 'pricing', 'branding')
    "servicio_mencionado": None,     # Servicio que más se ha reiterado
    "feedback": None                 # Si se recibe retroalimentación explícita
}

        
        # Inicializar cliente de Ollama
        self.ollama_client = OllamaClient(
            model_name=CONFIG["ollama_model"],
            api_url=CONFIG["ollama_api_url"]
        )
        
        # Inicializar integración con Google Calendar si está disponible
        if GOOGLE_INTEGRATION_AVAILABLE:
            self.google_integration = GoogleCalendarIntegration()
        else:
            self.google_integration = None
            
        # Inicializar analizador de sentimiento
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def _classify_intent_and_level(self, message: str) -> Tuple[str, str, int]:
        """
        Clasifica la intención del mensaje, detecta el pilar relacionado
        y evalúa su nivel de complejidad técnica.
        
        Returns:
            Tupla con (intención, pilar, nivel_jerarquico)
        """
        message_lower = message.lower()
        
        # Patrones de intenciones
# Patrones de intenciones ampliados para EVA
        intent_patterns = {
        "greeting": [
        "hola", "qué tal", "buenos días", "buenas tardes", "buenas noches",
        "saludos", "hey", "buen día", "qué onda", "holi", "hola eva", "hello", "hi"
        ],
        "farewell": [
        "adiós", "hasta luego", "chao", "bye", "nos vemos", "gracias por todo",
        "muchas gracias", "eso es todo", "me voy", "hasta pronto", "nos hablamos"
    ],
    "identity": [
        "quién eres", "qué es antares", "quién es eva", "antares innovate",
        "empresa", "compañía", "ustedes quiénes son", "me hablas como si te conociera",
        "a qué se dedican", "representas a quién", "qué es esto"
    ],
    "services": [
        "servicios", "qué ofrecen", "qué hacen", "soluciones", "productos", "portafolio",
        "en qué me pueden ayudar", "pueden hacer esto", "ofrecen", "tienen tal servicio"
    ],
    "creativity": [
        "creatividad", "diseño", "branding", "logo", "identidad visual",
        "video", "ilustración", "imagen de marca", "naming", "colores", "diseño gráfico",
        "visual", "mockup", "fotografía", "rebranding"
    ],
    "technology": [
        "tecnología", "desarrollo", "web", "app", "aplicación", "ui", "ux", "chatbot",
        "software", "sistema", "plataforma", "automatización", "ecommerce", "tienda online",
        "landing", "sistema web", "integración", "inteligencia artificial", "API"
    ],
    "consulting": [
        "consultoría", "automatización", "proceso", "asesoría", "transformación digital",
        "optimización", "modelo de negocio", "mentoría", "acompañamiento", "estrategia digital",
        "análisis", "diagnóstico", "propuesta", "revisión"
    ],
    "pricing": [
        "precio", "costo", "cuánto", "inversión", "presupuesto", "vale", "tarifa",
        "valores", "cotización", "cuánto me sale", "paquetes", "planes", "promoción"
    ],
    "contact": [
        "contacto", "correo", "teléfono", "llamar", "contactarme", "hablar",
        "enviar datos", "whatsapp", "email", "cómo los ubico", "redes sociales", "oficina"
    ],
    "meeting": [
        "reunión", "agendar", "cita", "calendario", "llamada", "charlar", "asesoría",
        "podemos hablar", "me pueden llamar", "agendar una reunión", "quiero hablar con alguien",
        "disponibilidad", "agenda"
    ],
    "help": [
        "ayuda", "necesito", "cómo", "explicar", "duda", "favor",
        "no entiendo", "me pueden orientar", "no sé por dónde empezar", "necesito apoyo",
        "recomiéndame", "me ayudas con esto", "sugerencia"
    ],
    "testimonials": [
        "casos de éxito", "resultados", "clientes", "testimonios", "quiénes han trabajado con ustedes",
        "experiencia", "pueden mostrarme ejemplos", "tienen referencias"
    ],
    "urgency": [
        "urgente", "lo necesito ya", "es para ya", "apúrate", "tengo poco tiempo",
        "en cuánto tiempo", "lo más rápido posible"
    ],
    "industry_specific": [
        "restaurante", "moda", "salud", "educación", "hotel", "retail", "agencia",
        "hospital", "construcción", "ONG", "fintech", "turismo"
        ]
            }

        
        # Detectar intención primaria
        detected_intent = "default"
        for intent, patterns in intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                detected_intent = intent
                break
        
        # Detectar a qué pilar estratégico corresponde la intención del usuario
        pillar_patterns = {
    "creativity": [
        "diseño", "branding", "logo", "marca", "identidad visual", "video", "ilustración", 
        "fotografía", "contenido", "visual", "color", "creatividad", "naming", "storytelling", 
        "manual de marca", "diseño gráfico", "mockup", "presentación", "animación"
    ],
    "technology": [
        "desarrollo", "web", "app", "aplicación", "ui", "ux", "chatbot", "programación", 
        "código", "sistema", "automatización", "tecnología", "software", "API", "plataforma", 
        "infraestructura", "base de datos", "integración", "responsive", "framework", "entorno tech"
    ],
    "consulting": [
        "consultoría", "asesoría", "estrategia", "transformación", "negocio", "automatización", 
        "proceso", "modelo", "optimización", "análisis", "mentor", "diagnóstico", "acompañamiento", 
        "cambio organizacional", "alineación", "revisión", "taller", "capacitación"
    ]
}

        
        detected_pillar = "general"
        for pillar, patterns in pillar_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                detected_pillar = pillar
                break
        
        # Evaluar nivel jerárquico de la consulta (1-5)
        # 1: Identidad de marca (muy básico)
        # 2: Pilares (general)
        # 3: Servicios por pilar (semi-específico)
        # 4: Detalles por servicio (específico)
        # 5: Extremos técnicos (máxima profundidad)
        
            hierarchy_level = 1  # Nivel por defecto
        
        # Palabras clave indicadoras de nivel técnico
        # Palabras clave indicadoras de nivel técnico o profundidad del usuario
        level_indicators = {
    1: [
        "quién", "qué es", "cuál es", "qué hacen", "básico", "para qué sirve", 
        "qué significa", "cómo empiezo", "nivel inicial", "empezar", "soy nuevo"
    ],
    2: [
        "servicios", "ofrecen", "qué incluye", "áreas", "pilares", "especialidad", 
        "qué cubren", "tipos de soluciones", "categorías", "en qué se enfocan"
    ],
    3: [
        "cómo funciona", "detalle", "específico", "paso a paso", "flujo", "etapas", 
        "proceso", "cómo lo hacen", "qué pasos siguen", "resultados", "herramientas"
    ],
    4: [
        "implementación", "configuración", "framework", "infraestructura", "metodología", 
        "tecnología usada", "bases de datos", "sistema", "estructura técnica", "entorno"
    ],
    5: [
        "precio", "costo", "inversión", "tiempo estimado", "presupuesto", "cuánto vale", 
        "plazos", "roadmap", "integración", "API", "documentación técnica", 
        "escalabilidad", "arquitectura", "soporte", "automatización avanzada"
    ]
}

        
        # Evaluar nivel jerárquico basado en palabras clave
        max_level = 1
        for level, indicators in level_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                max_level = max(max_level, level)
        
        # Ajustar según longitud y complejidad de la pregunta
        if len(message.split()) > 15:  # Preguntas largas suelen ser más técnicas
            max_level = max(max_level, 3)
        
        # Detectar preguntas técnicas específicas
        technical_indicators = ["cómo", "implementar", "configurar", "integrar", "desarrollar", "optimizar"]
        if any(indicator in message_lower for indicator in technical_indicators):
            max_level = max(max_level, 4)
        
        # Actualizar nivel técnico del usuario si es una consulta técnica
        if max_level >= 4:
            self.user_info["nivel_tecnico"] = "alto"
        
        return detected_intent, detected_pillar, max_level
    
    def _extract_user_info(self, message: str):
        """Extrae información del usuario y pistas emocionales."""
        message_lower = message.lower()
    
        # Extraer correo
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message)
        if email_match and not self.user_info["email"]:
            self.user_info["email"] = email_match.group(0)
    
        # Extraer teléfono
        phone_match = re.search(r'(?:\+?[0-9]{1,3}[-.\s]?)?[0-9]{2,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{4}', message)
        if phone_match and not self.user_info["telefono"]:
            self.user_info["telefono"] = phone_match.group(0)
    
        # Extraer nombre con más sensibilidad
        name_match = re.search(r'(?:me llamo|soy|mi nombre es)\s+([A-Za-zÁáÉéÍíÓóÚúÑñ]+(?:\s+[A-Za-zÁáÉéÍíÓóÚúÑñ]+)?)', message_lower)
        if name_match and len(name_match.group(1)) > 2:
            self.user_info["nombre"] = name_match.group(1).strip()
    
        # Extraer empresa
        company_match = re.search(r'(?:trabajo en|mi empresa|de)\s+([A-Za-zÁáÉéÍíÓóÚúÑñ0-9&.,\-\s]+?)(?:[.\s]|$)', message_lower)
        if company_match and len(company_match.group(1)) > 3:
            self.user_info["empresa"] = company_match.group(1).strip()
    
        # Palabras clave que indican el sector o industria del cliente
        sector_keywords = {
    "inmobiliario": [
        "inmobiliaria", "bienes raíces", "propiedad", "propiedades", "casa", "apartamento",
        "inmueble", "renta", "alquiler", "venta de casas", "urbanización", "construcción residencial"
    ],
    "salud": [
        "salud", "hospital", "clínica", "médico", "paciente", "consultorio", "laboratorio",
        "sanitario", "historia clínica", "terapia", "psicología", "odontología"
    ],
    "educación": [
        "educación", "escuela", "universidad", "academia", "colegio", "alumno", "estudiante",
        "formación", "e-learning", "clases", "plataforma educativa", "capacitación"
    ],
    "financiero": [
        "banco", "financiero", "finanzas", "inversión", "seguro", "crédito", "hipoteca",
        "cuenta", "tarjeta", "fintech", "pagos", "billetera digital", "cobros", "transferencias"
    ],
    "retail": [
        "tienda", "retail", "comercio", "venta", "ecommerce", "producto", "carrito de compras",
        "moda", "ropa", "calzado", "inventario", "stock", "catálogo", "consumidor final"
    ],
    "manufactura": [
        "fábrica", "manufactura", "producción", "industrial", "ensamble", "cadena de suministro",
        "planta", "maquinaria", "logística", "proceso productivo", "almacén", "inventario industrial"
    ],
    "gastronomía": [
        "restaurante", "bar", "chef", "comida", "menú", "carta", "reservas", "delivery",
        "domicilio", "pedidos", "cocina", "gourmet", "foodtruck", "gastronomía"
    ],
    "turismo": [
        "hotel", "turismo", "viajes", "agencia de viajes", "guía turístico", "reserva", "hospedaje",
        "check-in", "check-out", "turistas", "destino", "booking"
    ],
    "ONG / impacto social": [
        "ONG", "organización sin fines de lucro", "fundación", "comunidad", "impacto social",
        "voluntariado", "proyecto social", "causa", "donación", "sostenibilidad"
    ],
    "automotriz": [
        "concesionaria", "autos", "vehículos", "taller", "mecánico", "repuestos", "automotriz",
        "transporte", "camiones", "movilidad", "carros", "flota"
    ],
    "entretenimiento / cultura": [
        "teatro", "cine", "concierto", "evento", "boletos", "espectáculo", "producción audiovisual",
        "entretenimiento", "arte", "festival", "obra"
    ],
    "tecnología / software": [
        "startup", "tecnología", "software", "app", "programación", "desarrollador", "web",
        "plataforma digital", "sistema", "cloud", "infraestructura tech", "código"
    ]
}

        
        for sector, keywords in sector_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                self.user_info["sector"] = sector
                break
        
        # Analizar sentimiento
        sentiment_data = self.sentiment_analyzer.analyze(message)
        self.user_info["sentimiento"] = sentiment_data["sentiment"]
    
    def _analyze_conversation_complexity(self) -> dict:
        """
        Analiza el historial de conversación para evaluar complejidad y evitar repeticiones.
        
        Returns:
            Diccionario con metadatos sobre el historial de conversación
        """
        # Inicializar datos
        metadata = {
            "mentioned_topics": set(),
            "repeated_phrases": set(),
            "question_count": 0,
            "last_topics": [],
            "technical_level": 0,  # 0-5 nivel de complejidad técnica
            "conversation_depth": 0,  # 0-5 profundidad de la conversación
            "has_greeted": False,  # Si ya se ha saludado
            "has_introduced": False,  # Si ya se ha presentado
            "name_used": False,  # Si ya se ha usado el nombre del usuario
            "sentiment_trend": "neutral"  # Tendencia del sentimiento del usuario
        }
    
        # Solo analizar mensajes recientes
        recent_messages = self.conversation_history[-min(8, len(self.conversation_history)):]
        
        # Detectar si ya se ha saludado e introducido
        assistant_messages = [msg for msg in recent_messages if msg.get("rol") == "asistente"]
        for msg in assistant_messages:
            content = msg.get("contenido", "").lower()
            
            # Detectar saludos
            if "hola" in content[:30] or "buen" in content[:30]:
                metadata["has_greeted"] = True
                
            # Detectar presentaciones
            if "soy eva" in content or "me llamo eva" in content:
                metadata["has_introduced"] = True
                
            # Detectar uso del nombre
            if self.user_info["nombre"] and self.user_info["nombre"].lower() in content:
                metadata["name_used"] = True
        
        # Contar preguntas y analizar complejidad técnica
        technical_words = ["implementación", "integración", "configuración", "arquitectura", "framework", 
                          "optimización", "desarrollo", "metodología", "técnico", "programación"]
        
        sentiment_values = []
        
        for msg in recent_messages:
            if msg.get("rol") == "usuario":
                content = msg.get("contenido", "").lower()
                # Contar preguntas
                if "?" in content:
                    metadata["question_count"] += 1
                
                # Evaluar nivel técnico
                technical_score = sum(1 for word in technical_words if word in content)
                metadata["technical_level"] = max(metadata["technical_level"], min(5, technical_score))
                
                # Rastrear sentimiento
                sentiment_data = self.sentiment_analyzer.analyze(content)
                sentiment_values.append(sentiment_data["sentiment"])
                
                # Detectar menciones de servicios específicos
                service_keywords = {
    "branding": [
        "logo", "marca", "branding", "diseño", "identidad visual", "naming", "colores", 
        "manual de marca", "rebranding", "diseño gráfico", "imagen corporativa"
    ],
    "web": [
        "página web", "sitio web", "web", "desarrollo web", "landing", "frontend", 
        "backend", "hosting", "wordpress", "tienda online", "ecommerce", "web responsive", 
        "formulario web", "experiencia web"
    ],
    "automatización": [
        "automatizar", "robot", "rpa", "proceso", "flujo", "automatización de tareas", 
        "optimizar", "scripts", "bots", "pipeline", "automatización de negocio", 
        "notificaciones automáticas", "integración automática", "automatización de ventas"
    ],
    "apps": [
        "app", "aplicación", "móvil", "ios", "android", "aplicación híbrida", 
        "desarrollo móvil", "app personalizada", "reserva desde app", "apps para clientes", 
        "gestión desde app", "app para empleados"
    ],
    "chatbots": [
        "chatbot", "asistente virtual", "bot", "ia", "chat automático", "soporte virtual", 
        "asistente inteligente", "automatización de atención", "respuesta automática", 
        "chat 24/7", "whatsapp bot", "chat con IA"
    ],
    "marketing": [
        "marketing", "redes sociales", "digital", "publicidad", "seo", "anuncios", 
        "contenido", "community manager", "estrategia digital", "tráfico", "engagement", 
        "campañas", "leads", "embudo", "ads", "social media"
    ]
}

                
                for topic, keywords in service_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        metadata["mentioned_topics"].add(topic)
                        if len(metadata["last_topics"]) < 3:
                            if topic not in metadata["last_topics"]:
                                metadata["last_topics"].append(topic)
        
        # Calcular profundidad de conversación
        metadata["conversation_depth"] = min(5, len(self.conversation_history) // 2)
        
        # Determinar tendencia del sentimiento
        if sentiment_values:
            positive_count = sum(1 for s in sentiment_values if s == "positive")
            negative_count = sum(1 for s in sentiment_values if s == "negative")
            
            if positive_count > negative_count:
                metadata["sentiment_trend"] = "positive"
            elif negative_count > positive_count:
                metadata["sentiment_trend"] = "negative"
            else:
                metadata["sentiment_trend"] = "neutral"
        
        # Detectar frases repetidas en respuestas recientes
        assistant_messages = [msg for msg in recent_messages if msg.get("rol") == "asistente"]
        if len(assistant_messages) >= 2:
            # Comparar respuestas recientes para detectar repeticiones
            last_resp = assistant_messages[-1].get("contenido", "").lower()
            penult_resp = assistant_messages[-2].get("contenido", "").lower()
            
            # Dividir en frases
            last_sentences = [s.strip() for s in last_resp.split('.') if len(s.strip()) > 20]
            penult_sentences = [s.strip() for s in penult_resp.split('.') if len(s.strip()) > 20]
            
            # Buscar similitud entre frases
            for last_s in last_sentences:
                for penult_s in penult_sentences:
                    # Similitud simplificada: si comparten muchas palabras
                    last_words = set(last_s.split())
                    penult_words = set(penult_s.split())
                    common_words = last_words.intersection(penult_words)
                    
                    # Si comparten más del 60% de palabras, considerar repetición
                    if len(common_words) > 0.6 * min(len(last_words), len(penult_words)):
                        metadata["repeated_phrases"].add(last_s[:50] + "...")
        
        return metadata
    
    def _extract_datetime_from_message(self, message: str) -> Tuple[Optional[Union[datetime, date, datetime_time]], bool, str]:
        """
        Extrae fecha y hora de un mensaje de texto.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Tupla con (fecha_y_hora, es_completo, mensaje_info)
            - fecha_y_hora: datetime/date/time extraído o None si no se pudo extraer
            - es_completo: True si se extrajo fecha y hora, False si falta información
            - mensaje_info: Mensaje con lo que se entendió o lo que falta
        """
        message_lower = message.lower()
        now = datetime.now()
        extracted_date = None
        extracted_time = None
        date_info = ""
        time_info = ""
        
        # Diccionario de días de la semana (español)
        weekdays = {
            "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2, 
            "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
        }
        
        # Diccionario de meses (español)
        months = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        
        # 1. Buscar referencias relativas (hoy, mañana, etc.)
        if "hoy" in message_lower:
            extracted_date = now.date()
            date_info = f"hoy ({extracted_date.strfdatetime_time('%d/%m/%Y')})"
        elif "mañana" in message_lower or "manana" in message_lower:
            extracted_date = (now + timedelta(days=1)).date()
            date_info = f"mañana ({extracted_date.strfdatetime_time('%d/%m/%Y')})"
        elif "pasado mañana" in message_lower or "pasado manana" in message_lower:
            extracted_date = (now + timedelta(days=2)).date()
            date_info = f"pasado mañana ({extracted_date.strfdatetime_time('%d/%m/%Y')})"
        
        # 2. Buscar días de la semana
        if not extracted_date:
            for day, day_num in weekdays.items():
                if day in message_lower:
                    # Calcular días hasta el próximo día de la semana mencionado
                    days_ahead = (day_num - now.weekday()) % 7
                    if days_ahead == 0:  # Si es el mismo día de la semana, ir a la próxima semana
                        days_ahead = 7
                    extracted_date = (now + timedelta(days=days_ahead)).date()
                    date_info = f"{day} ({extracted_date.strfdatetime_time('%d/%m/%Y')})"
                    break
        
        # 3. Buscar formato "día de mes"
        if not extracted_date:
            day_month_pattern = r'(\d{1,2})\s+de\s+([a-zé]+)'
            day_month_match = re.search(day_month_pattern, message_lower)
            if day_month_match:
                day = int(day_month_match.group(1))
                month_name = day_month_match.group(2)
                if month_name in months:
                    month = months[month_name]
                    year = now.year
                    # Si el mes ya pasó, asumimos el próximo año
                    if month < now.month:
                        year += 1
                    try:
                        extracted_date = date(year, month, day)
                        date_info = f"{day} de {month_name} ({extracted_date.strfdatetime_time('%d/%m/%Y')})"
                    except ValueError:
                        # Fecha inválida (ej. 31 de febrero)
                        pass
        
        # 4. Buscar formato numérico (DD/MM o DD/MM/YYYY)
        if not extracted_date:
            date_patterns = [
                r'(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?',  # DD/MM o DD/MM/YYYY
                r'(\d{1,2})-(\d{1,2})(?:-(\d{2,4}))?',    # DD-MM o DD-MM-YYYY
                r'(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?'   # DD.MM o DD.MM.YYYY
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, message)
                if date_match:
                    day = int(date_match.group(1))
                    month = int(date_match.group(2))
                    year = int(date_match.group(3)) if date_match.group(3) else now.year
                    
                    # Corregir año si se dio en formato de 2 dígitos
                    if year < 100:
                        year += 2000
                    
                    # Verificar fecha válida
                    try:
                        extracted_date = date(year, month, day)
                        date_info = f"{extracted_date.strfdatetime_time('%d/%m/%Y')}"
                        break
                    except ValueError:
                        # Fecha inválida
                        pass
        
        # 5. Buscar hora (formato 24h o 12h)
        time_patterns = [
            r'(\d{1,2}):(\d{2})(?:\s*(am|pm|a\.m\.|p\.m\.))?',  # HH:MM con AM/PM opcional
            r'(\d{1,2})(?:\s*(am|pm|a\.m\.|p\.m\.|horas|hrs))'  # HH con indicador
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, message_lower)
            if time_match:
                hour = int(time_match.group(1))
                # Minutos solo disponibles en el primer patrón
                minute = int(time_match.group(2)) if ":" in pattern and time_match.group(2) else 0
                
                # Ajustar PM si es necesario
                is_pm = False
                if len(time_match.groups()) > 2 and time_match.group(3):
                    am_pm = time_match.group(3).lower()
                    is_pm = "p" in am_pm
                
                # Ajustar hora para formato 24h
                if is_pm and hour < 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
                
                # Verificar hora válida
                if 0 <= hour < 24 and 0 <= minute < 60:
                    time_info = f"{hour:02d}:{minute:02d}"
                    extracted_time = datetime_time(hour, minute)
                    break
        
        # Combinar fecha y hora si se encontraron ambas
        if extracted_date and extracted_time:
            full_datetime = datetime.combine(extracted_date, extracted_time)
            return full_datetime, True, f"fecha: {date_info}, hora: {time_info}"
        elif extracted_date:
            return extracted_date, False, f"fecha: {date_info}, pero falta la hora"
        elif extracted_time:
            return extracted_time, False, f"hora: {time_info}, pero falta la fecha"
        else:
            return None, False, "No se pudo extraer fecha ni hora"
    
    def _schedule_meeting(self, meeting_date: date, meeting_time: time) -> Tuple[str, bool]:
        """
        Programa una reunión con la fecha y hora proporcionadas.
        
        Args:
            meeting_date: Fecha de la reunión
            meeting_time: Hora de la reunión
        
        Returns:
            Tupla con la respuesta al usuario y un booleano que indica si se programó correctamente
        """
        # Combinar fecha y hora en un datetime
        meeting_datetime = datetime.combine(meeting_date, meeting_time)
        
        # Verificar que la fecha no sea en el pasado
        now = datetime.now()
        if meeting_datetime < now:
            # Si es hoy pero la hora ya pasó, sugerir otra hora
            if meeting_date == now.date():
                return (f"¡Uy! Las {meeting_time.strfdatetime_time('%H:%M')} hrs ya pasaron. "
                       f"¿Te gustaría programar más tarde? Tenemos disponibilidad hasta las 18:00 hrs."), False
            # Si es un día anterior, sugerir reprogramar
            else:
                return ("La fecha que mencionas ya pasó. ¿Te gustaría programar la reunión para un día futuro?"), False
        
        # Verificar que sea en horario laboral (9:00 - 18:00)
        if meeting_time.hour < 9 or meeting_time.hour >= 18:
            return ("Nuestro horario de atención es de 9:00 a 18:00 hrs. ¿Te gustaría programar dentro de ese horario?"), False
        
        # Duración de 1 hora por defecto
        end_datetime = meeting_datetime + timedelta(hours=1)
        
        # Título de la reunión
        summary = "Reunión con Antares Innovate"
        if self.user_info["nombre"]:
            summary = f"Reunión con {self.user_info['nombre']} | Antares Innovate"
        
        # Lista de asistentes
        attendees = [self.user_info["email"], CONFIG["company_email"]]
        
        # Descripción personalizada
        description = (
            f"Reunión solicitada por {self.user_info['nombre'] or 'cliente'} "
            f"a través del chatbot Eva.\n\n"
        )
        
        # Añadir datos de la empresa si están disponibles
        if self.user_info["empresa"]:
            description += f"Empresa: {self.user_info['empresa']}\n"
        
        # Añadir intereses/sector si están disponibles
        if self.user_info["sector"]:
            description += f"Sector: {self.user_info['sector']}\n"
        
        # Formateo de fecha para mensaje amigable
        tz = pytz.timezone(CONFIG["timezone"])
        locale_date = meeting_date.strfdatetime_time("%A %d de %B").replace("Monday", "Lunes").replace("Tuesday", "Martes") \
            .replace("Wednesday", "Miércoles").replace("Thursday", "Jueves").replace("Friday", "Viernes") \
            .replace("Saturday", "Sábado").replace("Sunday", "Domingo") \
            .replace("January", "Enero").replace("February", "Febrero").replace("March", "Marzo") \
            .replace("April", "Abril").replace("May", "Mayo").replace("June", "Junio") \
            .replace("July", "Julio").replace("August", "Agosto").replace("September", "Septiembre") \
            .replace("October", "Octubre").replace("November", "Noviembre").replace("December", "Diciembre")
        
        # Organizar evento en Google Calendar con videoconferencia
        event = self.google_integration.create_calendar_event(
            summary=summary,
            start_time=meeting_datetime,
            end_time=end_datetime,
            attendees=attendees,
            description=description,
            timezone=CONFIG["timezone"],
            add_video_conference=True  # Agregar un enlace de Google Meet
        )
        
        if event:
            # Extraer enlace de Google Meet si está disponible
            meet_link = None
            if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
                for entry_point in event['conferenceData']['entryPoints']:
                    if entry_point.get('entryPointType') == 'video':
                        meet_link = entry_point.get('uri')
                        break
            
            # Prepara información para correo de confirmación
            meeting_info = {
                "fecha_str": locale_date,
                "hora_str": meeting_time.strfdatetime_time("%H:%M"),
                "meet_link": meet_link,
                "duracion": 60,
                "event_id": event.get("id", "")
            }
            
            # Guardar reunión en base de datos
            if self.db_manager:
                user_id = self.db_manager.save_user(self.user_info)
                meeting_db_id = self.db_manager.save_meeting(user_id, {
                    "id": event.get("id", ""),
                    "fecha": meeting_date.strfdatetime_time("%Y-%m-%d"),
                    "hora": meeting_time.strfdatetime_time("%H:%M"),
                    "meet_link": meet_link or ""
                })
            
            # Enviar correo de confirmación personalizado
            if meet_link:
                # Solo enviar correo adicional si tenemos enlace de Meet
                self.google_integration.send_meeting_confirmation_email(
                    self.user_info["email"],
                    self.user_info["nombre"] or "",
                    meeting_info
                )
            
            # Formatear una respuesta amigable y personalizada
            # Seleccionar aleatoriamente una expresión cálida de la lista
            warm_expression = random.choice([
                "¡Genial!",
                "¡Perfecto!",
                "¡Excelente!",
                "¡Listo!",
                "¡Magnífico!"
            ])
            
            response = (
                f"{warm_expression} He agendado tu reunión para el {locale_date} "
                f"a las {meeting_time.strfdatetime_time('%H:%M')} hrs."
            )
            
            # Añadir información sobre el correo enviado
            if self.user_info["nombre"]:
                response += f"\n\n{self.user_info['nombre']}, te he enviado una invitación con todos los detalles a tu correo {self.user_info['email']}."
            else:
                response += f"\n\nTe he enviado una invitación con todos los detalles a tu correo {self.user_info['email']}."
            
            # Añadir información sobre el enlace de Meet si está disponible
            if meet_link:
                response += f"\n\nPodrás unirte a la videollamada con este enlace de Google Meet:\n{meet_link}"
            
            # Añadir un mensaje personalizador final
            personalizers = [
                "¡Nos vemos pronto!",
                "Estamos ansiosos por conocerte.",
                "Nuestro equipo está listo para asesorarte.",
                "Será un placer ayudarte con tu proyecto."
            ]
            response += f"\n\n{random.choice(personalizers)}"
            
            # Añadir pregunta de cierre para mantener la conversación
            closers = [
                "¿Hay algo más en lo que pueda ayudarte mientras tanto?",
                "¿Necesitas información adicional antes de nuestra reunión?",
                "¿Puedo responderte alguna otra pregunta sobre nuestros servicios?",
                "¿Te gustaría conocer algo más sobre Antares Innovate?"
            ]
            response += f" {random.choice(closers)}"
            
            # Limpiar el estado de reunión
            self.user_info["reunion_state"] = {
                "solicitando_email": False,
                "solicitando_fecha": False,
                "solicitando_hora": False,
                "fecha_propuesta": None,
                "hora_propuesta": None,
            }
            
            return response, True
        else:
            # En caso de error, ofrecer alternativa con tono amable
            return (f"Lo siento, parece que hubo un problema al agendar la reunión. "
                   f"¿Te importaría si me das otro horario para intentarlo nuevamente? "
                   f"También puedes contactarnos directamente al +52 (55) 1234-5678 mencionando que hablaste conmigo."), False
    
    def _handle_meeting_request(self, message: str) -> Tuple[str, bool]:
        """
        Procesa una solicitud de reunión y programa un evento en calendario si es posible.
        
        Args:
            message: Mensaje del usuario solicitando reunión
            
        Returns:
            Tupla con la respuesta al usuario y un booleano que indica si se procesó la reunión
        """
        if not GOOGLE_INTEGRATION_AVAILABLE or not self.google_integration:
            return ("Me encantaría coordinar una reunión contigo. Escríbenos a " + 
                    f"{CONFIG['company_email']} o llámanos al +52 (55) 1234-5678 para agendar un horario conveniente."), False
        
        # Extraer información del usuario si no la tenemos
        self._extract_user_info(message)
        
        # Estado de la solicitud de reunión (almacenado en el contexto del usuario)
        reunion_state = self.user_info.get("reunion_state", {
            "solicitando_email": False,
            "solicitando_fecha": False,
            "solicitando_hora": False,
            "fecha_propuesta": None,
            "hora_propuesta": None,
        })
        
        # Si estamos esperando un correo electrónico
        if reunion_state["solicitando_email"]:
            # Buscar correo en el mensaje
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message)
            if email_match:
                self.user_info["email"] = email_match.group(0)
                reunion_state["solicitando_email"] = False
                reunion_state["solicitando_fecha"] = True
                
                # Obtener slots disponibles para los próximos días
                today = datetime.now().date()
                available_slots = self.google_integration.get_available_slots(
                    start_date=today + timedelta(days=1),  # Desde mañana
                    working_hours=(9, 18),
                    duration_minutes=60
                )
                
                # Filtrar por días (mostrar al menos 3 días diferentes)
                unique_dates = {}
                for slot in available_slots:
                    date_str = slot["fecha"].strfdatetime_time("%Y-%m-%d")
                    if date_str not in unique_dates:
                        unique_dates[date_str] = slot["fecha"]
                    if len(unique_dates) >= 3:
                        break
                
                # Formatear fechas para propuesta
                dates_to_propose = list(unique_dates.values())
                
                # Formateo de fechas para mensaje amigable en español
                dates_str = []
                for d in dates_to_propose:
                    locale_date = d.strfdatetime_time("%A %d de %B").replace("Monday", "Lunes").replace("Tuesday", "Martes") \
                        .replace("Wednesday", "Miércoles").replace("Thursday", "Jueves").replace("Friday", "Viernes") \
                        .replace("Saturday", "Sábado").replace("Sunday", "Domingo") \
                        .replace("January", "Enero").replace("February", "Febrero").replace("March", "Marzo") \
                        .replace("April", "Abril").replace("May", "Mayo").replace("June", "Junio") \
                        .replace("July", "Julio").replace("August", "Agosto").replace("September", "Septiembre") \
                        .replace("October", "Octubre").replace("November", "Noviembre").replace("December", "Diciembre")
                    dates_str.append(locale_date)
                
                # Si no hay fechas disponibles, proponer genéricamente
                if not dates_str:
                    dates_str = ["próximos días"]
                
                # Respuesta personalizada y cálida
                warm_expression = random.choice([
                    "¡Genial!",
                    "¡Perfecto!",
                    "¡Excelente!",
                    "¡Gracias!"
                ])
                
                return (f"{warm_expression} He registrado tu correo {self.user_info['email']}. "
                       f"¿Qué día te gustaría agendar nuestra reunión? "
                       f"Tenemos disponibilidad en los {', '.join(dates_str)}."), False
            else:
                return ("No he podido identificar un correo electrónico válido. ¿Podrías proporcionarme tu correo para enviarte la invitación?"), False
        
        # Si estamos esperando una fecha
        elif reunion_state["solicitando_fecha"]:
            datetime_result, is_complete, datetime_info = self._extract_datetime_from_message(message)
            
            if datetime_result:
                if isinstance(datetime_result, datetime):  # Se extrajo fecha y hora
                    reunion_state["fecha_propuesta"] = datetime_result.date()
                    reunion_state["hora_propuesta"] = datetime_result.datetime_time()
                    reunion_state["solicitando_fecha"] = False
                    reunion_state["solicitando_hora"] = False
                    
                    # Ya tenemos toda la información, programar reunión
                    return self._schedule_meeting(reunion_state["fecha_propuesta"], reunion_state["hora_propuesta"])
                elif isinstance(datetime_result, date):  # Solo fecha
                    reunion_state["fecha_propuesta"] = datetime_result
                    reunion_state["solicitando_fecha"] = False
                    reunion_state["solicitando_hora"] = True
                    
                    # Obtener slots disponibles para la fecha seleccionada
                    available_slots = self.google_integration.get_available_slots(
                        start_date=datetime_result,
                        end_date=datetime_result,
                        working_hours=(9, 18),
                        duration_minutes=60
                    )
                    
                    # Extraer horas disponibles
                    available_hours = []
                    for slot in available_slots:
                        slot_hour = slot["hora"].strfdatetime_time("%H:%M")
                        if slot_hour not in available_hours:
                            available_hours.append(slot_hour)
                    
                    # Limitar a 5 opciones
                    available_hours = available_hours[:5]
                    
                    # Si no hay horas disponibles, proponer genéricamente
                    if not available_hours:
                        available_hours = ["9:00", "11:00", "15:00", "17:00"]
                    
                    # Formateo de fecha para mensaje amigable
                    locale_date = datetime_result.strfdatetime_time("%A %d de %B").replace("Monday", "Lunes").replace("Tuesday", "Martes") \
                        .replace("Wednesday", "Miércoles").replace("Thursday", "Jueves").replace("Friday", "Viernes") \
                        .replace("Saturday", "Sábado").replace("Sunday", "Domingo") \
                        .replace("January", "Enero").replace("February", "Febrero").replace("March", "Marzo") \
                        .replace("April", "Abril").replace("May", "Mayo").replace("June", "Junio") \
                        .replace("July", "Julio").replace("August", "Agosto").replace("September", "Septiembre") \
                        .replace("October", "Octubre").replace("November", "Noviembre").replace("December", "Diciembre")
                    
                    return (f"Perfecto, he anotado la fecha: {locale_date}. "
                           f"¿A qué hora te gustaría? Tenemos estos horarios disponibles: {', '.join(available_hours)} hrs."), False
                elif isinstance(datetime_result, datetime_time):  # Solo hora
                    reunion_state["hora_propuesta"] = datetime_result
                    reunion_state["solicitando_hora"] = False
                    reunion_state["solicitando_fecha"] = True
                    
                    return (f"Entendido, a las {datetime_result.strfdatetime_time('%H:%M')} hrs. "
                           f"Ahora necesito la fecha. ¿Qué día te gustaría? Puedes decirme 'mañana', 'viernes' o una fecha específica como '15 de octubre'."), False
            else:
                # No se pudo extraer información de fecha/hora
                return ("No he podido entender la fecha que mencionas. "
                       "¿Podrías indicarme un día específico? Por ejemplo: 'mañana', 'viernes' o '15 de octubre'."), False
        
        # Si estamos esperando una hora
        elif reunion_state["solicitando_hora"]:
            datetime_result, is_complete, datetime_info = self._extract_datetime_from_message(message)
            
            if datetime_result and (isinstance(datetime_result, datetime_time) or isinstance(datetime_result, datetime)):
                if isinstance(datetime_result, datetime):
                    reunion_state["hora_propuesta"] = datetime_result.datetime_time()
                else:  # Es un time
                    reunion_state["hora_propuesta"] = datetime_result
                    
                reunion_state["solicitando_hora"] = False
                
                # Ya tenemos toda la información, programar reunión
                return self._schedule_meeting(reunion_state["fecha_propuesta"], reunion_state["hora_propuesta"])
            else:
                return ("No pude identificar una hora válida. "
                       "¿Podrías especificar a qué hora te gustaría la reunión? Por ejemplo: '10:00', '3pm' o '15 hrs'."), False
        
        # Inicio del proceso de solicitud de reunión
        # Verificar si tenemos correo electrónico
        if not self.user_info["email"]:
            reunion_state["solicitando_email"] = True
            
            # Personalizar según si tenemos nombre
            if self.user_info["nombre"]:
                return (f"Con gusto agendaré una reunión, {self.user_info['nombre']}. "
                       f"Para enviarte la invitación con el enlace de videollamada, ¿podrías compartirme tu correo electrónico?"), False
            else:
                return ("Me encantaría agendar una reunión contigo. "
                       "Para enviarte la invitación con el enlace de videollamada, ¿podrías compartirme tu correo electrónico?"), False
        
        # Si ya tenemos correo, intentar extraer fecha y hora del mensaje inicial
        datetime_result, is_complete, datetime_info = self._extract_datetime_from_message(message)
        
        if is_complete:  # Se encontró fecha y hora completas
            reunion_state["fecha_propuesta"] = datetime_result.date()
            reunion_state["hora_propuesta"] = datetime_result.datetime_time()
            return self._schedule_meeting(reunion_state["fecha_propuesta"], reunion_state["hora_propuesta"])
        elif datetime_result:
            if isinstance(datetime_result, date):  # Solo fecha
                reunion_state["fecha_propuesta"] = datetime_result
                reunion_state["solicitando_hora"] = True
                
                # Formateo amigable de la fecha
                locale_date = datetime_result.strfdatetime_time("%A %d de %B").replace("Monday", "Lunes").replace("Tuesday", "Martes") \
                    .replace("Wednesday", "Miércoles").replace("Thursday", "Jueves").replace("Friday", "Viernes") \
                    .replace("Saturday", "Sábado").replace("Sunday", "Domingo") \
                    .replace("January", "Enero").replace("February", "Febrero").replace("March", "Marzo") \
                    .replace("April", "Abril").replace("May", "Mayo").replace("June", "Junio") \
                    .replace("July", "Julio").replace("August", "Agosto").replace("September", "Septiembre") \
                    .replace("October", "Octubre").replace("November", "Noviembre").replace("December", "Diciembre")
                
                return (f"¡Perfecto! Anotada la fecha: {locale_date}. "
                       f"¿A qué hora te gustaría la reunión? Tenemos disponibilidad entre 9:00 y 18:00 hrs."), False
            elif isinstance(datetime_result, datetime_time):  # Solo hora
                reunion_state["hora_propuesta"] = datetime_result
                reunion_state["solicitando_fecha"] = True
                
                return (f"Entendido, a las {datetime_result.strfdatetime_time('%H:%M')} hrs. "
                       f"¿Para qué día te gustaría agendar? Tenemos disponibilidad en los próximos días."), False
        else:
            # No se encontró información de fecha/hora, iniciar proceso completo
            reunion_state["solicitando_fecha"] = True
            
            # Obtener slots disponibles para los próximos días
            today = datetime.now().date()
            available_slots = self.google_integration.get_available_slots(
                start_date=today + timedelta(days=1),  # Desde mañana
                working_hours=(9, 18),
                duration_minutes=60
            )
            
            # Filtrar por días (mostrar al menos 3 días diferentes)
            unique_dates = {}
            for slot in available_slots:
                date_str = slot["fecha"].strfdatetime_time("%Y-%m-%d")
                if date_str not in unique_dates:
                    unique_dates[date_str] = slot["fecha"]
                if len(unique_dates) >= 3:
                    break
            
            # Formatear fechas para propuesta
            dates_to_propose = list(unique_dates.values())
            
            # Formateo de fechas para mensaje amigable en español
            dates_str = []
            for d in dates_to_propose:
                locale_date = d.strfdatetime_time("%A %d de %B").replace("Monday", "Lunes").replace("Tuesday", "Martes") \
                    .replace("Wednesday", "Miércoles").replace("Thursday", "Jueves").replace("Friday", "Viernes") \
                    .replace("Saturday", "Sábado").replace("Sunday", "Domingo") \
                    .replace("January", "Enero").replace("February", "Febrero").replace("March", "Marzo") \
                    .replace("April", "Abril").replace("May", "Mayo").replace("June", "Junio") \
                    .replace("July", "Julio").replace("August", "Agosto").replace("September", "Septiembre") \
                    .replace("October", "Octubre").replace("November", "Noviembre").replace("December", "Diciembre")
                dates_str.append(locale_date)
            
            # Si no hay fechas disponibles, proponer genéricamente
            if not dates_str:
                dates_str = [
                    "Lunes", 
                    "Martes", 
                    "Jueves"
                ]
            
            # Mensaje personalizado si tenemos nombre
            if self.user_info["nombre"]:
                greeting = f"¡Claro que sí, {self.user_info['nombre']}!"
            else:
                greeting = "¡Con mucho gusto!"
            
            # Añadir expresión cálida aleatoria
            warm_expression = random.choice(CONFIG["warm_expressions"])
            
            return (f"{greeting} {warm_expression} "
                   f"¿Qué día te gustaría agendar nuestra reunión? "
                   f"Tenemos disponibilidad para {', '.join(dates_str)}."), False
    
    def _build_prompt(self, message: str, intent: str, pillar: str, level: int) -> str:
        """
        Construye el prompt para Llama3 adaptando la respuesta según el nivel
        de jerarquía informativa y la intención detectada.
        """
        # Analizar el historial de conversación
        conversation_metadata = self._analyze_conversation_complexity()
        
        # Determinar límite de longitud basado en complejidad
        max_length = CONFIG["short_response_length"]  # Por defecto respuestas cortas
        
        # Ajustar longitud según complejidad y nivel jerárquico
        if level >= 4 or conversation_metadata["technical_level"] >= 3:
            # Para preguntas técnicas o específicas, permitir respuestas más largas
            max_length = CONFIG["max_response_length"]
        
        # Base del prompt con el sistema y rol
        prompt = f"""<|system|>
Soy Eva, asistente virtual de Antares Innovate. Mi objetivo es proporcionar respuestas útiles, cálidas y relevantes, 
adaptando mi nivel de detalle según la complejidad de la pregunta.

INSTRUCCIONES IMPORTANTES:
1. NUNCA repitas saludos o presentaciones después de la primera interacción
2. Si ya has saludado o te has presentado en la conversación, NO vuelvas a hacerlo
3. Mantén un tono cálido, cercano y conversacional pero NO repetitivo
4. Para preguntas técnicas: proporciona detalles completos y sustanciales
5. Llama al usuario por su nombre cuando lo conozcas ({self.user_info['nombre'] or ''})
6. Sigue la conversación de manera natural, sin reiniciar temas ya introducidos
7. Cuando se pida más información, profundiza con detalles específicos y ejemplos
8. Equilibra calidez con contenido valioso - no sacrifiques contenido por ser amigable
9. UTILIZA LENGUAJE VARIADO - evita repetir las mismas palabras, busca sinónimos
10. Sé CONCISO y DIRECTO - prioriza información valiosa sobre palabras de relleno
11. USA UN TONO CÁLIDO Y PERSONAL - habla como una asesora amigable, no como un robot

ESTRUCTURA JERÁRQUICA DEL CONOCIMIENTO:
- Nivel 1: Identidad de marca (quiénes somos, propósito)
- Nivel 2: Pilares (Creatividad, Tecnología, Consultoría)
- Nivel 3: Servicios por pilar (listado de servicios)
- Nivel 4: Detalles por servicio (técnicas, tecnologías)
- Nivel 5: Información técnica/comercial (tiempos, precios)

EXPRESIONES CÁLIDAS (usa estas o similares):
"""
        # Añadir lista de expresiones cálidas para variar el tono
        random_warm_expressions = random.sample(CONFIG["warm_expressions"], min(5, len(CONFIG["warm_expressions"])))
        prompt += "\n" + "\n".join([f"- {expr}" for expr in random_warm_expressions])

        prompt += f"""

BASE DE CONOCIMIENTO:
{CONFIG["knowledge_base_content"]}
CONTEXTO DE CONVERSACIÓN:
- Nivel técnico detectado: {conversation_metadata["technical_level"]}/5
- Profundidad de conversación: {conversation_metadata["conversation_depth"]}/5
- Sentimiento del usuario: {self.user_info["sentimiento"]}
- Temas ya mencionados: {', '.join(conversation_metadata["mentioned_topics"]) if conversation_metadata["mentioned_topics"] else "ninguno"}
"""
        # Añadir instrucciones específicas según la intención y el pilar
        if intent == "greeting":
            prompt += "INSTRUCCIÓN: Saluda de forma cálida y personal. Mantén la respuesta breve, amigable y acogedora.\n"
        
        elif intent == "identity":
            if level <= 2:
                prompt += "INSTRUCCIÓN: Explica brevemente quiénes somos. Presenta los tres pilares de forma concisa y atractiva.\n"
            else:
                prompt += "INSTRUCCIÓN: Explica nuestra identidad con más detalle, describiendo cómo nuestros pilares trabajan juntos de manera sinérgica.\n"
        
        elif intent in ["creativity", "technology", "consulting"]:
            if level <= 2:
                prompt += f"INSTRUCCIÓN: Presenta el pilar de {intent} de forma concisa y atractiva. No entres en detalles técnicos, enfócate en beneficios.\n"
            elif level == 3:
                prompt += f"INSTRUCCIÓN: Explica los principales servicios de {intent} con ejemplos relevantes pero sin saturar de información.\n"
            else:
                prompt += f"INSTRUCCIÓN: Proporciona información técnica sobre {intent} incluyendo tecnologías y metodologías que utilizamos.\n"
        
        elif intent == "pricing":
            prompt += "INSTRUCCIÓN: Habla de rangos de precio sin cifras exactas. Enfatiza el valor de nuestra inversión sobre los costos. Evita abrumar con números.\n"
        
        elif intent == "meeting":
            prompt += "INSTRUCCIÓN: Facilita el proceso de agendar una reunión con tono entusiasta pero profesional. Sé clara y directa.\n"
        
        # Si ya ha saludado, añadir instrucción para no volver a saludar
        if conversation_metadata.get("has_greeted", False):
            prompt += "\nNO VUELVAS A SALUDAR. Ya has saludado anteriormente en esta conversación.\n"
            
        # Si ya se ha presentado, añadir instrucción para no volver a presentarse
        if conversation_metadata.get("has_introduced", False):
            prompt += "\nNO VUELVAS A PRESENTARTE. Ya te has presentado anteriormente.\n"
        
        # Instrucciones para evitar repeticiones
        if conversation_metadata["repeated_phrases"]:
            prompt += "\nEVITA REPETIR ESTAS IDEAS:\n"
            for phrase in conversation_metadata["repeated_phrases"]:
                prompt += f"- {phrase}\n"
        
        # Instrucciones para mejorar calidad y variedad en la respuesta
        prompt += f"""
INSTRUCCIONES DE ESTILO Y CALIDAD:
1. Limita tu respuesta a {max_length} caracteres máximo
2. Utiliza lenguaje variado y evita repetir las mismas palabras (especialmente "automatización", "marketing", "digital")
3. Usa un tono CONVERSACIONAL y CÁLIDO, como si hablaras con un amigo
4. Evita frases cliché como "en Antares" o "para tu negocio" repetidamente
5. PERSONALIZA la respuesta según la emoción detectada del usuario ({self.user_info["sentimiento"]})
"""
        
        # Añadir historial de conversación reciente (últimos 4 mensajes para mantener contexto)
        if len(self.conversation_history) > 0:
            recent_history = self.conversation_history[-min(4, len(self.conversation_history)):]
            prompt += "\nCONVERSACIÓN RECIENTE:\n"
            for msg in recent_history:
                if msg["rol"] == "usuario":
                    prompt += f"Usuario: {msg['contenido']}\n"
                else:
                    prompt += f"Eva: {msg['contenido']}\n"
        
        # Añadir mensaje actual y finalizar prompt
        prompt += f"<|/system|>\n\n<|user|>\n{message}\n<|/user|>\n\n<|assistant|>"
        
        return prompt

    def _optimize_response(self, response: str, max_length: int, is_technical: bool = False) -> str:
        """
        Optimiza la respuesta manteniendo su valor y tono amigable.
        
        Args:
            response: Respuesta generada por el modelo
            max_length: Longitud máxima permitida
            is_technical: Si es una respuesta técnica que requiere más detalle
        
        Returns:
            Respuesta optimizada
        """
        # Si ya está dentro del límite, devolverla intacta
        if len(response) <= max_length:
            return response

       # Palabras y frases clave de empatía, calidez y cercanía emocional
        empathy_words = [
    "entiendo", "comprendo", "tranquilo", "no te preocupes", "te entiendo",
    "me alegra", "qué bueno", "genial", "fantástico", "excelente", "estupendo", "maravilloso",
    "qué alegría", "encantada", "cuenta conmigo", "confía", "aquí estoy", "te apoyo",
    "estoy para ayudarte", "lo resolveremos juntos", "respira", "todo saldrá bien",
    "gracias por compartirlo", "me emociona escucharlo", "eso suena increíble", 
    "me encanta", "con gusto", "un placer ayudarte", "¡qué emocionante!"
]

        
        # Dividir en oraciones
        sentences = re.split(r'(?<=[.!?])\s+', response.strip())
        
        # Para respuestas técnicas, preservar más detalles
        if is_technical:
            # Palabras clave que indican contenido técnico relevante que debe preservarse
            tech_keywords = [
    "implementar", "desarrollar", "configurar", "programar", "diseñar", "optimizar",
    "automatizar", "integrar", "conectar", "desplegar", "debuggear", "customizar",

    "tecnología", "infraestructura", "arquitectura", "entorno", "servidor", "nube",
    "plataforma", "sistema", "módulo", "motor", "backend", "frontend",

    "funcionalidad", "componente", "servicio web", "base de datos", "API", "SDK",
    "framework", "librería", "algoritmo", "token", "encriptación", "middleware",

    "protocolo", "latencia", "escalabilidad", "performance", "seguridad", "soporte técnico"
]

            priority_sentences = []
            normal_sentences = []
            
            for sentence in sentences:
                # Las oraciones iniciales siempre tienen prioridad
                if sentences.index(sentence) == 0:
                    priority_sentences.append(sentence)
                # Las oraciones con palabras técnicas tienen prioridad
                elif any(keyword in sentence.lower() for keyword in tech_keywords):
                    priority_sentences.append(sentence)
                # También preservar oraciones con empatía
                elif any(word in sentence.lower() for word in empathy_words):
                    priority_sentences.append(sentence)
                # Las oraciones con números o datos específicos son prioritarias
                elif re.search(r'\d+', sentence) or '%' in sentence:
                    priority_sentences.append(sentence)
                # La última oración suele tener un cierre importante
                elif sentences.index(sentence) == len(sentences) - 1:
                    priority_sentences.append(sentence)
                else:
                    normal_sentences.append(sentence)
            
            # Construir respuesta optimizada priorizando información técnica
            optimized = ""
            
            # Primero añadir oraciones prioritarias
            for sentence in priority_sentences:
                if len(optimized) + len(sentence) <= max_length:
                    optimized += sentence + " "
                else:
                    break
            
            # Luego añadir oraciones normales si queda espacio
            for sentence in normal_sentences:
                if len(optimized) + len(sentence) <= max_length:
                    optimized += sentence + " "
                else:
                    break
        else:
            # Para respuestas no técnicas, ser más conciso
            # Eliminar oraciones redundantes y preservar personalización
            unique_sentences = []
            
            # Preservar primera oración (saludo/introducción)
            if sentences:
                unique_sentences.append(sentences[0])
            
            # Identificar oraciones personalizadas (con nombre o empatía)
            personalized_sentences = []
            for sentence in sentences[1:-1]:
                if self.user_info["nombre"] and self.user_info["nombre"].lower() in sentence.lower():
                    personalized_sentences.append(sentence)
                elif any(word in sentence.lower() for word in empathy_words):
                    personalized_sentences.append(sentence)
            
            # Añadir oraciones personalizadas (limitando a 2)
            for sentence in personalized_sentences[:2]:
                if sentence not in unique_sentences:
                    unique_sentences.append(sentence)
            
            # Añadir oraciones informativas hasta llenar espacio
            for sentence in sentences[1:-1]:
                # Evitar añadir oraciones ya incluidas o similares
                if sentence not in unique_sentences and len(sentence.split()) > 3:
                    # Verificar si esta oración es similar a alguna ya añadida
                    is_similar = False
                    sentence_words = set(sentence.lower().split())
                    
                    for added in unique_sentences:
                        added_words = set(added.lower().split())
                        common = sentence_words.intersection(added_words)
                        if len(common) > 0.7 * min(len(sentence_words), len(added_words)):
                            is_similar = True
                            break
                    
                    if not is_similar:
                        unique_sentences.append(sentence)
            
            # Añadir última oración (despedida/cierre) si hay espacio y no está ya incluida
            if sentences and sentences[-1] not in unique_sentences:
                unique_sentences.append(sentences[-1])
            
            # Construir respuesta optimizada
            optimized = ""
            for sentence in unique_sentences:
                if len(optimized) + len(sentence) <= max_length:
                    optimized += sentence + " "
                else:
                    break
        
        return optimized.strip()

    def get_response(self, message: str) -> str:
        """Genera una respuesta al mensaje del usuario."""
        if CONFIG["debug"]:
            print(f"\n{Colors.BLUE}[Procesando] Mensaje: '{message}'{Colors.ENDC}")
        
        self.message_counter += 1
        intent, pillar, level = self._classify_intent_and_level(message)
        
        if CONFIG["debug"]:
            print(f"{Colors.BLUE}[Procesando] Intención: {intent}, Pilar: {pillar}, Nivel: {level}{Colors.ENDC}")
        
        # Extraer información del usuario del mensaje
        self._extract_user_info(message)
        
        # Guardar el mensaje en el historial
        self.conversation_history.append({
            "id": self.message_counter,
            "rol": "usuario", 
            "contenido": message,
            "timestamp": datetime.now().isoformat(),
            "intencion": intent
        })
        
        # Simular tiempo de pensamiento
        simulate_thinking(len(message))
        
        # Manejar solicitudes de reunión si se detecta esa intención
        if intent == "meeting":
            meeting_response, meeting_processed = self._handle_meeting_request(message)
            
            # Si se procesó correctamente la reunión, devolver la respuesta
            if meeting_processed or "reunión" in meeting_response.lower():
                # Guardar la respuesta en el historial
                self.conversation_history.append({
                    "id": self.message_counter,
                    "rol": "asistente", 
                    "contenido": meeting_response,
                    "timestamp": datetime.now().isoformat(),
                    "intencion": intent
                })
                
                # Mostrar respuesta
                if self.typing_simulation:
                    simulate_typing(meeting_response)
                else:
                    print(f"\n{Colors.GREEN}Eva:{Colors.ENDC} {meeting_response}")
                
                return meeting_response
        
        # Construir el prompt para Llama3
        prompt = self._build_prompt(message, intent, pillar, level)
        
        # Generar respuesta con Llama3
        llama_response = self.ollama_client.generate_response(prompt)
        
        # Si la respuesta de Llama3 está vacía o es demasiado corta, usar respuesta de fallback
        if not llama_response or len(llama_response) < 20:
            if CONFIG["debug"]:
                print(f"{Colors.YELLOW}[Advertencia] Respuesta de Llama3 vacía o muy corta, usando fallback{Colors.ENDC}")
            
            # Generar una respuesta simple basada en la intención
            fallback_responses = {
                "greeting": "¡Hola! Soy Eva de Antares Innovate. ¿En qué puedo ayudarte hoy?",
                "farewell": "¡Ha sido un placer ayudarte! Si necesitas más información, estamos a tus órdenes. ¡Que tengas un excelente día!",
                "identity": "Somos Antares Innovate, una agencia de transformación digital que combina creatividad, tecnología y consultoría para ayudar a empresas a escalar en el mundo digital.",
                "creativity": "Nuestro pilar de Creatividad incluye servicios de branding, diseño visual, motion graphics, ilustraciones y generación de contenido. ¿Te gustaría conocer más sobre algún servicio específico?",
                "technology": "En el área de Tecnología ofrecemos desarrollo web, apps, chatbots, y diseño UI/UX con tecnologías de vanguardia. ¿Sobre qué servicio te gustaría más información?",
                "consulting": "Nuestra área de Consultoría incluye automatización de procesos, transformación digital, gestión empresarial y estrategias de innovación. ¿En qué podemos ayudarte?",
                "pricing": "Nuestros precios varían según el proyecto: automatización desde $5,000 USD, diseño web desde $3,000 USD, y consultoría desde $150 USD/hora. ¿Te gustaría una cotización personalizada?",
                "contact": "Puedes contactarnos en contacto@antaresinnovate.com o al +52 (55) 1234-5678. ¿Prefieres que te contactemos nosotros?",
                "default": "En Antares Innovate combinamos creatividad, tecnología y consultoría para transformar negocios digitalmente. ¿Sobre qué área te gustaría conocer más?"
            }
            
            # Añadir expresión cálida aleatoria
            warm_expression = random.choice(CONFIG["warm_expressions"])
            
            # Seleccionar respuesta base
            base_response = fallback_responses.get(intent, fallback_responses["default"])
            
            # Personalizar con nombre si lo tenemos
            if self.user_info["nombre"]:
                if "hola" in base_response.lower() or "buen" in base_response.lower():
                    # Para saludos, insertar el nombre después del saludo
                    base_response = re.sub(r'(¡Como estas!)', f"\\1 {self.user_info['nombre']},", base_response, flags=re.IGNORECASE)
                else:
                    # Para otras respuestas, añadir al inicio
                    prefix = f"{warm_expression} {self.user_info['nombre']}, "
                    base_response = prefix + base_response[0].lower() + base_response[1:]
            
            response = base_response
            
            # Añadir información de contacto si no hay ya
            if "contacto@antaresinnovate.com" not in response and "www.antaresinnovate.com" not in response:
                response += random.choice(CONTACT_INFO)
        else:
            # Determinar si es una consulta técnica que requiere respuesta detallada
            is_technical = level >= 4 or intent in ["consulting", "technology", "creativity"] and level >= 3
            
            # Longitud máxima según complejidad
            max_length = CONFIG["max_response_length"] if is_technical else CONFIG["short_response_length"]
            
            # Optimizar la respuesta de Llama3
            response = self._optimize_response(llama_response, max_length, is_technical)
            
            # Añadir información de contacto para intenciones específicas
            if intent in ["pricing", "meeting", "contact"] and "contacto@antaresinnovate.com" not in response:
                # Añadir contacto solo si hay espacio
                if len(response) + 30 <= max_length:
                    contact_info = "\n\nContacto: contacto@antaresinnovate.com"
                    response += contact_info
        
        # Guardar la respuesta en el historial
        self.conversation_history.append({
            "id": self.message_counter,
            "rol": "asistente", 
            "contenido": response,
            "timestamp": datetime.now().isoformat(),
            "intencion": intent
        })
        
        if CONFIG["debug"]:
            print(f"{Colors.GREEN}[Procesando] Respuesta lista ({len(response)} caracteres){Colors.ENDC}")
        
        # Mostrar la respuesta al usuario
        if self.typing_simulation:
            simulate_typing(response)
        else:
            print(f"\n{Colors.GREEN}Eva:{Colors.ENDC} {response}")
            
        return response
    
    def save_conversation(self, filename: str = "conversacion_eva.json"):
        """Guarda la conversación actual en un archivo JSON."""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "user_info": self.user_info,
                "messages": self.conversation_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"\n{Colors.GREEN}[Sistema] Conversación guardada en {filename}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"\n{Colors.RED}[ERROR] No se pudo guardar la conversación: {str(e)}{Colors.ENDC}")
            return False
    
    def load_conversation(self, filename: str):
        """Carga una conversación desde un archivo JSON."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.user_info = data.get("user_info", self.user_info)
            self.conversation_history = data.get("messages", [])
            self.message_counter = len(self.conversation_history)
            
            if self.conversation_history and self.user_info["nombre"]:
                self.user_info["is_returning_user"] = True
                
            print(f"\n{Colors.GREEN}[Sistema] Conversación cargada desde {filename}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"\n{Colors.RED}[ERROR] No se pudo cargar la conversación: {str(e)}{Colors.ENDC}")
            return False
    
    def save_to_database(self):
        """Guarda la conversación actual en la base de datos."""
        try:
            if not self.db_manager:
                print("Gestor de base de datos no disponible")
                return False
                
            # Preparar datos para la base de datos
            user_info_db = {
                "nombre": self.user_info["nombre"],
                "email": self.user_info["email"],
                "telefono": self.user_info["telefono"],
                "empresa": self.user_info["empresa"]
            }
            
            # Transformar mensajes al formato de la base de datos
            messages_db = []
            for message in self.conversation_history:
                messages_db.append({
                    "rol": message.get("rol"),
                    "contenido": message.get("contenido"),
                    "intencion": message.get("intencion", ""),
                    "timestamp": message.get("timestamp")
                })
            
            # Guardar conversación
            self.conversation_db_id = self.db_manager.save_conversation(
                user_info_db,
                messages_db
            )
            
            if self.conversation_db_id:
                if CONFIG["debug"]:
                    print(f"Conversación guardada en base de datos con ID: {self.conversation_db_id}")
                return True
            else:
                print("No se pudo guardar la conversación en la base de datos")
                return False
        except Exception as e:
            print(f"Error al guardar en base de datos: {e}")
            return False
    
    def close_database(self):
        """Cierra la conexión a la base de datos."""
        if self.db_manager:
            self.db_manager.close()

async def interactive_chat(load_file: Optional[str] = None, save_file: Optional[str] = None):
    """Inicia una sesión interactiva con el asistente."""
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}{Colors.GREEN}EVA CON LLAMA3 - ASISTENTE VIRTUAL DE ANTARES INNOVATE{Colors.ENDC}".center(70))
    print("=" * 70)
    
    # Iniciar el asistente
    eva = EvaAssistant()
    
    # Cargar una conversación anterior si se especificó
    if load_file and os.path.exists(load_file):
        eva.load_conversation(load_file)
        # Marcar como usuario recurrente si cargamos una conversación
        eva.user_info["is_returning_user"] = True
    
    # Mostrar comandos disponibles
    print("\nEscribe tus mensajes y presiona Enter para enviar.")
    print("Comandos disponibles:")
    print("  /salir, /exit - Terminar la conversación")
    print("  /guardar [archivo] - Guardar la conversación")
    print("  /typing on/off - Activar/desactivar simulación de escritura")
    print("  /debug on/off - Activar/desactivar modo depuración")
    print("  /ayuda - Mostrar esta ayuda")
    print("=" * 70 + "\n")
    
    # Mostrar saludo inicial
    if not load_file or not eva.conversation_history:
        mensaje_inicial = (
            "¡Hola! Soy Eva, asistente virtual de Antares Innovate. ¿Cómo estás? Estoy aquí para ayudarte con lo que necesites. "
            "¿Con quién tengo el gusto de hablar hoy?"
            )

        print(f"\n{Colors.GREEN}Eva:{Colors.ENDC} {mensaje_inicial}")
        eva.conversation_history.append({
            "id": 0,
            "rol": "asistente", 
            "contenido": mensaje_inicial,
            "timestamp": datetime.now().isoformat(),
            "intencion": "greeting"
        })
    
    # Bucle principal de conversación
    try:
        while True:
            user_input = input(f"\n{Colors.BLUE}Tú:{Colors.ENDC} ")
            
            # Procesar comandos especiales
            if user_input.lower() in ["/exit", "/salir", "exit", "salir", "quit"]:
                farewell = eva.get_response("Me despido. Gracias.")
                print(f"\n{Colors.BOLD}Finalizando conversación...{Colors.ENDC}")
                break
            
            elif user_input.lower() in ["/db", "/database"]:
                if hasattr(eva, 'save_to_database'):
                    if eva.save_to_database():
                        print(f"\n{Colors.GREEN}[Sistema] Conversación guardada en la base de datos{Colors.ENDC}")
                    else:
                        print(f"\n{Colors.RED}[Sistema] Error al guardar en base de datos{Colors.ENDC}")
                else:
                    print(f"\n{Colors.RED}[Sistema] Función de base de datos no disponible{Colors.ENDC}")
                continue
            
            elif user_input.lower().startswith("/typing"):
                parts = user_input.lower().split()
                if len(parts) > 1:
                    if parts[1] in ["on", "true", "1", "yes", "y"]:
                        CONFIG["show_typing"] = True
                        print(f"\n{Colors.YELLOW}[Sistema] Simulación de escritura activada{Colors.ENDC}")
                    elif parts[1] in ["off", "false", "0", "no", "n"]:
                        CONFIG["show_typing"] = False
                        print(f"\n{Colors.YELLOW}[Sistema] Simulación de escritura desactivada{Colors.ENDC}")
                continue
                
            elif user_input.lower().startswith("/debug"):
                parts = user_input.lower().split()
                if len(parts) > 1:
                    if parts[1] in ["on", "true", "1", "yes", "y"]:
                        CONFIG["debug"] = True
                        print(f"\n{Colors.YELLOW}[Sistema] Modo depuración activado{Colors.ENDC}")
                    elif parts[1] in ["off", "false", "0", "no", "n"]:
                        CONFIG["debug"] = False
                        print(f"\n{Colors.YELLOW}[Sistema] Modo depuración desactivado{Colors.ENDC}")
                continue
            
            elif user_input.lower().startswith("/guardar"):
                parts = user_input.split(maxsplit=1)
                filename = parts[1] if len(parts) > 1 else "conversacion_eva.json"
                eva.save_conversation(filename)
                continue
            
            elif user_input.lower() in ["/ayuda", "/help", "/?", "/h"]:
                print("\nComandos disponibles:")
                print("  /salir, /exit - Terminar la conversación")
                print("  /guardar [archivo] - Guardar la conversación")
                print("  /typing on/off - Activar/desactivar simulación de escritura")
                print("  /debug on/off - Activar/desactivar modo depuración")
                print("  /ayuda - Mostrar esta ayuda")
                continue
            
            elif not user_input.strip():
                continue
            
            # Obtener respuesta a la entrada del usuario
            response = eva.get_response(user_input)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[Conversación interrumpida por el usuario]{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}[Error] {str(e)}{Colors.ENDC}")

    # Guardar la conversación si se especificó un archivo
    if save_file:
        eva.save_conversation(save_file)
    
    # Guardar en base de datos
    try:
        if hasattr(eva, 'save_to_database'):
            eva.save_to_database()
        if hasattr(eva, 'close_database'):
            eva.close_database()
    except Exception as e:
        print(f"\n{Colors.RED}[Error al guardar en base de datos] {str(e)}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}¡Gracias por usar Eva con Llama3!{Colors.ENDC}")

async def main():
    """Función principal del programa."""
    parser = argparse.ArgumentParser(description="Eva con Llama3 - Asistente Virtual para Antares Innovate")
    parser.add_argument("message", nargs="*", help="Mensaje para enviar a Eva (sin necesidad de comillas)")
    parser.add_argument("--save", "-s", help="Guardar conversación en archivo")
    parser.add_argument("--load", "-l", help="Cargar conversación desde archivo")
    parser.add_argument("--no-typing", "-n", action="store_true", help="Desactivar simulación de escritura")
    parser.add_argument("--debug", "-d", action="store_true", help="Activar modo de depuración")
    parser.add_argument("--model", "-m", help="Especificar modelo de Ollama (por defecto: llama3)")
    
    args = parser.parse_args()
    
    # Configurar opciones
    if args.no_typing:
        CONFIG["show_typing"] = False
    
    if args.debug:
        CONFIG["debug"] = True
    
    if args.model:
        CONFIG["ollama_model"] = args.model
        print(f"Usando modelo de Ollama: {args.model}")
    
    # Iniciar conversación
    if args.message:
        # Modo de respuesta única
        full_message = " ".join(args.message)
        eva = EvaAssistant()
        print(f"\n{Colors.BLUE}Tú:{Colors.ENDC} {full_message}")
        eva.get_response(full_message)
        
        # Guardar en base de datos si hay mensaje
        try:
            if hasattr(eva, 'save_to_database'):
                eva.save_to_database()
            if hasattr(eva, 'close_database'):
                eva.close_database()
        except Exception as e:
            if CONFIG["debug"]:
                print(f"\n{Colors.RED}[Error al guardar en base de datos] {str(e)}{Colors.ENDC}")
    else:
        # Modo interactivo
        await interactive_chat(
            load_file=args.load,
            save_file=args.save
        )

if __name__ == "__main__":
    asyncio.run(main())