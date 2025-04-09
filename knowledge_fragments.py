"""
knowledge_fragments.py - Base de conocimiento centralizada para Eva con Llama3

Este módulo:
1. Contiene la configuración global (reemplaza CONFIG en eva_llama_14.py)
2. Organiza la base de conocimiento en fragmentos más pequeños y manejables
3. Implementa lienzos técnicos detallados por área (creatividad, desarrollo, marketing)
4. Proporciona funciones para seleccionar conocimiento relevante según intención y contexto

Autor: Antares Innovate
"""

# =============================================================================
# CONFIGURACIÓN GLOBAL - Reemplaza a CONFIG en eva_llama_14.py
# =============================================================================

# Configuración de tiempos de respuesta y simulación
MIN_RESPONSE_TIME = 0.4
MAX_RESPONSE_TIME = 1.2
CHAR_TYPING_SPEED = 0.01
SHOW_TYPING = True

# Mensajes para simular "pensamiento" mientras se genera la respuesta
THINKING_MESSAGES = [
    "Analizando tu consulta... 🔍", 
    "Procesando información... 💡", 
    "Buscando la mejor respuesta para ti... ✨",
    "Preparando una respuesta personalizada... 🌟",
    "Consultando nuestra base de conocimiento... 📚"
]

# Configuración de Ollama
DEBUG = True
OLLAMA_MODEL = "llama3"
OLLAMA_API_URL = "https://evaollama.loca.lt/api/generate"

# Límites de longitud para respuestas
MAX_RESPONSE_LENGTH = 600  # Límite para respuestas técnicas
SHORT_RESPONSE_LENGTH = 300  # Límite para respuestas simples

# Configuración del calendario y reuniones
GOOGLE_CREDENTIALS_FILE = "credentials.json"
GOOGLE_TOKEN_FILE = "token.json"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send"
]
COMPANY_EMAIL = "contacto@antaresinnovate.com"
CALENDAR_ID = "primary"
TIMEZONE = "America/Mexico_City"

# Información de contacto para fallback
CONTACT_INFO = [
    "\n\n📱 Puedes contactarnos al +52 (689) 331 2690.",
    "\n\n📧 Escríbenos a contacto@antaresinnovate.com.",
    "\n\n🌐 Visita www.antaresinnovate.com para más información."
]

# Expresiones cálidas actualizadas para un tono más natural y conversacional
WARM_EXPRESSIONS = [
    "¡Qué bueno que me preguntas! 😊",
    "Me encanta poder ayudarte con esto ✨",
    "Cuenta conmigo para esto 👍",
    "¿Te gustaría que empecemos hoy mismo?",
    "¡Genial! Me alegra que preguntes por esto",
    "Estoy aquí para facilitarte el proceso",
    "¡Perfecto! Vamos a resolver esto juntos",
    "¿Qué te parece si avanzamos con esta idea?",
    "¡Excelente pregunta! 👏",
    "Me encantaría hablar más sobre esto",
    "Estoy lista para ayudarte con tu proyecto ✅",
    "¿Quieres que te cuente más detalles?",
    "Podemos hacer este proyecto realidad",
    "Cuéntame más sobre lo que necesitas 😊",
    "¿En qué más puedo ayudarte hoy?",
    "¡Entiendo perfectamente! Muchos de nuestros clientes empiezan así",
    "No te preocupes, estamos aquí para guiarte en cada paso 🤝",
    "Suena como un proyecto interesante 🌟",
    "Me encanta tu idea, tiene mucho potencial",
    "¿Hay algo específico que te preocupe sobre este proyecto?"
]

# Plantillas de correo para reuniones
EMAIL_TEMPLATES = {
    "meeting_confirmation": {
        "subject": "¡Reunión confirmada con Antares Innovate! 📅",
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
                    <h1>¡Reunión Confirmada! 🎯</h1>
                </div>
                <div class="content">
                    <h2>¡Hola {{nombre}}! 👋</h2>
                    
                    <p>Tu reunión con Antares Innovate ha sido confirmada para:</p>
                    
                    <p><strong>📅 Fecha:</strong> {{fecha}}<br>
                    <strong>⏰ Hora:</strong> {{hora}} ({{timezone}})<br>
                    <strong>⏱️ Duración:</strong> {{duracion}} minutos</p>
                    
                    <p>Podrás unirte a través del siguiente enlace de Google Meet:</p>
                    
                    <p style="text-align: center;">
                        <a href="{{meet_link}}" class="button">Unirse a la reunión 💻</a>
                    </p>
                    
                    <p>Si no puedes asistir, por favor contáctanos con anticipación para reprogramar.</p>
                    
                    <p>¡Esperamos verte pronto! 🚀</p>
                    
                    <p>El equipo de Antares Innovate</p>
                </div>
                <div class="footer">
                    <p>Antares Innovate | contacto@antaresinnovate.com | +52 (689) 331 2690</p>
                </div>
            </div>
        </body>
        </html>
        """
    }
}

# =============================================================================
# FRAGMENTOS DE CONOCIMIENTO - Base de información organizada por secciones
# =============================================================================

KNOWLEDGE_FRAGMENTS = {
    "identidad": {
        "titulo": "IDENTIDAD DE MARCA",
        "contenido": """¡Hola! Somos Antares Innovate, una agencia de transformación digital creativa. Nos apasiona combinar creatividad, tecnología y consultoría para ayudar a empresas como la tuya a crecer en el mundo digital. Estamos en Colombia y USA para acompañarte en tu viaje digital. ✨"""
    },
    
    "pilares": {
        "titulo": "PILARES PRINCIPALES",
        "contenido": """Nos apoyamos en tres pilares fundamentales para impulsar tu negocio:

1. ✨ Creatividad: Diseño de marca y contenido que conecta emocionalmente con tu audiencia.
2. 💻 Tecnología: Soluciones digitales a medida que transforman tus ideas en realidad, desde sitios web hasta apps y chatbots.
3. 📊 Consultoría: Asesoramiento estratégico en transformación digital y automatización para optimizar tus procesos."""
    },
    
    "creatividad_servicios": {
        "titulo": "CREATIVIDAD - SERVICIOS",
        "contenido": """Nuestros servicios creativos están diseñados para hacer brillar tu marca:

• 🎨 Identidad visual única (logos memorables, paletas de colores y tipografías)
• 📒 Manuales de marca y Brandbooks que cuentan tu historia
• 📝 Storytelling visual que conecta emocionalmente
• 🎬 Producción de video y postproducción profesional
• ⚡ Motion graphics y animación 2D/3D que captura la atención
• 🖌️ Ilustraciones, concept art y vectores personalizados
• 🤖 Generación de contenido con IA para mantenerte a la vanguardia
• 📹 Comerciales y audiovisuales de alto impacto para tu audiencia"""
    },
    
    "tecnologia_servicios": {
        "titulo": "TECNOLOGÍA - SERVICIOS",
        "contenido": """Te ofrecemos soluciones tecnológicas adaptadas a tus necesidades:

• 💎 Diseño UI/UX premiado que encanta a los usuarios (Figma, prototipado, pruebas)
• 🌐 Desarrollo web con las últimas tecnologías (React, Next.js, Tailwind, WordPress)
• 📱 Apps web y móviles intuitivas y poderosas
• 🔄 Integración perfecta con APIs y sistemas externos
• 🤖 Chatbots inteligentes con personalidad (incluyendo audio y voz)
• 🏙️ Modelado y render 3D para experiencias web inmersivas"""
    },
    
    "consultoria_servicios": {
        "titulo": "CONSULTORÍA - SERVICIOS",
        "contenido": """Optimizamos tus procesos de negocio con estos servicios:

• ⚙️ Automatización de procesos empresariales (BPA) que ahorran tiempo y recursos
• 🤖 Automatización robótica (RPA) para tareas repetitivas
• 🔄 Integración de sistemas que elimina silos de información
• 📊 Desarrollo de flujos de trabajo más eficientes
• 💬 Chatbots y asistentes virtuales que mejoran la experiencia del cliente
• 📈 Gestión empresarial y digitalización para optimizar tu operación
• 💰 Modelos de negocio digitales adaptados a tu mercado
• 🚀 Consultoría en innovación y escalamiento para crecer sosteniblemente"""
    },
    
    "desarrollo_detalle": {
        "titulo": "DETALLES TÉCNICOS - DISEÑO Y DESARROLLO",
        "contenido": """Nuestro enfoque técnico en diseño y desarrollo incluye:

• 🎯 UI/UX: Diseño centrado en usuario con wireframes y prototipos interactivos que aseguran una experiencia fluida
• 🛠️ Desarrollo: Utilizamos React, Next.js, Tailwind, Node.js, Laravel y WordPress según tus necesidades específicas
• 📱 Apps: Creamos con React Native, PWA e integraciones API que funcionan perfectamente en cualquier dispositivo
• 🤖 Chatbots: Implementamos NLP, integración con WhatsApp, voz e IA generativa para una comunicación natural
• 🏙️ 3D: Experiencias inmersivas con Three.js, modelado, animación y visualización que impresionan"""
    },
    
    "automatizacion_detalle": {
        "titulo": "DETALLES TÉCNICOS - AUTOMATIZACIÓN",
        "contenido": """Nuestras soluciones de automatización transforman tu negocio:

• ⚙️ BPA: Transformamos tus operaciones completas, desde entrada de datos hasta informes, liberando el potencial de tu equipo.
• 🤖 RPA: Implementamos robots de software que realizan tareas repetitivas a alta velocidad y sin errores.
• 🔄 Integración: Conectamos tus aplicaciones eliminando silos de información para una visión unificada.
• 📊 Flujos de Trabajo: Creamos secuencias optimizadas con aprobaciones automáticas que agilizan decisiones.
• 📈 Beneficios tangibles: Nuestros clientes logran hasta 40% de reducción en costos operativos y eliminación virtual de errores."""
    },
    
    "precios": {
        "titulo": "INFORMACIÓN COMERCIAL",
        "contenido": """Nuestra inversión se adapta a proyectos de diferentes tamaños:

• 🤖 Automatización: Proyectos personalizados desde $5,000 USD adaptados a tu complejidad
• 🌐 Diseño web: Soluciones completas desde $3,000 USD con CMS incluido para tu gestión
• 📱 Apps: Desarrollo profesional desde $8,000 USD por plataforma con todas las funcionalidades
• 💬 Chatbots: Asistentes virtuales desde $3,000 USD con las integraciones que necesitas
• 📊 Consultoría: Asesoramiento experto a $150 USD/hora o proyectos integrales desde $10,000 USD

Cada propuesta es personalizada según tus objetivos específicos. ¿Te gustaría una cotización a medida?"""
    },
    
    "contacto": {
        "titulo": "CONTACTO",
        "contenido": """¿Listo para comenzar? Estamos a un mensaje de distancia:

📱 Tel: +52 (689) 331 2690
📧 Email: contacto@antaresinnovate.com
🌐 Web: www.antaresinnovate.com

¡Esperamos conocerte pronto y ayudarte a impulsar tu proyecto digital!"""
    }
}

# =============================================================================
# LIENZO TÉCNICO: CREATIVIDAD - Servicios detallados del área creativa
# =============================================================================

LIENZO_TECNICO_CREATIVIDAD = {
    "identidad_marca": {
        "servicios": "- 🎨 Diseño de logotipo y naming\n- 📒 Manual de identidad visual\n- 📑 Papelería corporativa física y digital\n- ✉️ Firmas de correo\n- 📊 Formatos corporativos (facturas, presentaciones, etc.)",
        "descripcion": "Construcción de marcas con coherencia visual y técnica. Entregables para impresión y uso digital. Se aplican reglas tipográficas, cromáticas y compositivas consistentes."
    },
    
    "personajes": {
        "servicios": "- 👤 Personajes en estilo cartoon, vectorial, realista\n- 🤖 IA para consistencia visual\n- 🎨 Uso de OpenArt, Freepik AI, Sora",
        "descripcion": "Desarrollo asistido por IA con prompts optimizados. Output para branding, producto, storytelling o motion. Integración multicanal."
    },
    
    "diseno_producto": {
        "servicios": "- 📦 Diseño gráfico aplicado a empaques, etiquetas y presentaciones de producto",
        "descripcion": "Desarrollo visual de producto desde prototipo hasta visualización final, integrando branding y necesidades técnicas."
    },
    
    "editorial": {
        "servicios": "- 📚 Revistas, módulos, brochures, cartillas\n- 📱 Material adaptable digital e impreso",
        "descripcion": "Diseño editorial con enfoque técnico (CMYK, márgenes, resolución). Maquetación para impresión o PDF interactivo."
    },
    
    "presentaciones": {
        "servicios": "- 🎯 PowerPoint, Word interactivo, Figma, video pitch",
        "descripcion": "Diseño de presentaciones de alto impacto visual y argumentativo. Animaciones, IA visual o narrada, formatos exportables para diferentes plataformas."
    },
    
    "contenido_rrss": {
        "servicios": "- 📅 Parrilla visual\n- 📹 Videos cortos (Reels)\n- 🎞️ Gifs, imágenes, storytelling visual",
        "descripcion": "Diseño de piezas para campañas, tanto orgánicas como pagadas. Adaptación a formatos dinámicos y algoritmos de engagement."
    },
    
    "concept_art": {
        "servicios": "- 🎨 Bocetos visuales de ideas, escenarios, personajes\n- 🖌️ Apoyo a proyectos de branding, audiovisual, juegos, apps",
        "descripcion": "Base visual conceptual para desarrollo de experiencias o marcas con estilo artístico definido (manual, vectorial, IA)."
    },
    
    "audiovisual": {
        "servicios": "- 📝 Guión, story board\n- 🎬 Producción física o virtual (IA)\n- 🎞️ Edición, montaje, etalonaje profesional\n- 🎵 Voz y música (IA y real)",
        "descripcion": "Producción integral desde la estrategia audiovisual hasta la postproducción. Integración de IA como Runway, Pika, ElevenLabs. Corrección de color, mezcla sonora, estilo visual coherente."
    },
    
    "motion": {
        "servicios": "- ⚡ Motion graphics, animación 2D/3D\n- 📱 Integración Lottie\n- 🎵 Lyrics videos",
        "descripcion": "Animación vectorial, gráfica o ilustrativa para explainer videos, redes, productos o plataformas. Exportación optimizada para web."
    },
    
    "ui_ux": {
        "servicios": "- 💎 Diseño de experiencia para apps, webs y plataformas\n- 📱 Prototipos navegables (Figma)\n- 🎬 Integraciones interactivas (video, animación, contenido personalizado)",
        "descripcion": "Enfoque en arquitectura de información, accesibilidad y estética. Testeos de usabilidad, mapas de empatía y recorridos de usuario. Diseño adaptable con integración de animación y contenido audiovisual."
    },
    
    "web_apps": {
        "servicios": "- 📱 Diseño responsive y mobile-first\n- 📲 UI para apps Android/iOS\n- 🔍 Landing pages con storytelling\n- 📊 Diseño escalable y modular",
        "descripcion": "Enfoque en fluidez, retención y conversión. Colaboración con desarrollo para entregables optimizados (SVGs, assets animados, prototipos). Adaptación al desarrollo con React, Next.js u otras stacks."
    },
    
    "3d_interaccion": {
        "servicios": "- 🏙️ Render de arquitectura/producto\n- 🔄 Integración con Spline + Next.js\n- 🌐 Experiencias inmersivas",
        "descripcion": "Generación de escenas y productos 3D navegables. Adaptación para visor web con performance optimizado. Uso de Blender y WebGL."
    }
}

# =============================================================================
# LIENZO TÉCNICO: DESARROLLO - Servicios detallados del área de desarrollo
# =============================================================================

LIENZO_TECNICO_DESARROLLO = {
    "desarrollo_web": {
        "servicios": "- 🌐 Sitios corporativos y landing pages\n- 📱 Aplicaciones web progresivas (PWA)\n- 🛒 E-commerce y plataformas de venta\n- 🔐 Intranets y portales de gestión\n- 📝 CMS personalizados",
        "descripcion": "Desarrollo frontend con React, Next.js y Tailwind CSS. Backend con Node.js, Python o PHP/Laravel según necesidades. Optimización SEO, rendimiento y UX. Despliegue en AWS, Vercel o infraestructura personalizada."
    },
    
    "aplicaciones_moviles": {
        "servicios": "- 📱 Apps nativas para iOS y Android\n- 🔄 Apps híbridas multiplataforma\n- 🏢 Apps empresariales con acceso a backend\n- 🔌 Integración con servicios externos\n- 🔄 Mantenimiento y actualizaciones",
        "descripcion": "Desarrollo nativo con Swift/Kotlin o híbrido con React Native/Flutter. Integración de funcionalidades como geolocalización, notificaciones push, autenticación segura, pagos in-app y acceso a hardware del dispositivo."
    },
    
    "arquitectura_sistemas": {
        "servicios": "- 🏗️ Diseño de arquitectura de software\n- 🔄 Microservicios y API REST/GraphQL\n- 💾 Bases de datos relacionales y NoSQL\n- ⚡ Caching y optimización de rendimiento\n- 📈 Escalabilidad y alta disponibilidad",
        "descripcion": "Diseño de sistemas escalables y mantenibles con arquiectura limpia y patrones adecuados. Implementación de CI/CD, infraestructura como código, y monitoreo. Bases de datos optimizadas para el caso de uso específico."
    },
    
    "devops": {
        "servicios": "- 🔄 Implementación de CI/CD\n- 🐳 Containerización con Docker/Kubernetes\n- 📝 Infraestructura como código (Terraform)\n- 📊 Monitoreo y alertas (Prometheus, Grafana)\n- 🚀 Automatización de despliegues",
        "descripcion": "Configuración de pipelines de integración continua y despliegue automatizado. Orquestación de contenedores para entornos de alta disponibilidad. Monitoreo proactivo con alertas personalizadas. Gestión eficiente de infraestructura."
    },
    
    "integraciones": {
        "servicios": "- 💳 Pasarelas de pago (Stripe, PayPal, etc.)\n- 🔌 APIs de terceros (Google, Microsoft, etc.)\n- 🏢 CRMs y ERPs (Salesforce, SAP, etc.)\n- 💬 Servicios de mensajería (Slack, WhatsApp)\n- ☁️ Servicios Cloud (AWS, Azure, GCP)",
        "descripcion": "Integración seamless con servicios externos mediante APIs. Manejo seguro de autenticación OAuth y claves API. Implementación de webhooks y eventos. Sincronización bidireccional de datos entre sistemas."
    },
    
    "ecommerce": {
        "servicios": "- 🛒 Tiendas online personalizadas\n- 🔌 Integraciones con WooCommerce/Shopify\n- 🛍️ Carritos de compra y checkout optimizado\n- 📦 Gestión de inventario y pedidos\n- 💳 Pasarelas de pago múltiples",
        "descripcion": "Plataformas de venta online optimizadas para conversión. Experiencia de usuario fluida en móvil y desktop. Integración con sistemas de logística y gestión de inventario. Análisis de abandono de carrito y estrategias de recuperación."
    },
    
    "cms": {
        "servicios": "- 🌐 WordPress con Gutenberg/Elementor\n- 🔌 Headless CMS (Strapi, Contentful)\n- 📝 CMS personalizados según necesidades\n- 🔄 Migración entre plataformas\n- 🔒 Optimización y seguridad",
        "descripcion": "Sistemas de gestión de contenido a medida del flujo de trabajo del cliente. Interfaces de administración intuitivas. Arquitecturas headless para máxima flexibilidad. Control granular de permisos y roles."
    },
    
    "seguridad": {
        "servicios": "- 🔍 Auditorías de seguridad\n- 🔒 Implementación HTTPS/SSL\n- 🛡️ Protección contra ataques comunes\n- 🔐 Gestión segura de autenticación\n- 🔏 Encriptación de datos sensibles",
        "descripcion": "Protección contra vulnerabilidades OWASP Top 10. Implementación de JWT, OAuth y autenticación MFA. Validación estricta de inputs y sanitización. Políticas de contraseñas robustas y gestión de sesiones seguras."
    },
    
    "ia_machine_learning": {
        "servicios": "- 🤖 Chatbots inteligentes\n- 📊 Análisis predictivo\n- 🎯 Sistemas de recomendación\n- 🔤 Procesamiento de lenguaje natural\n- 👁️ Visión computacional",
        "descripcion": "Integración de modelos de IA (OpenAI, Hugging Face) para automatización inteligente. Sistemas de recomendación basados en comportamiento de usuario. Automatización de procesos con NLP. Reconocimiento de imágenes y detección de objetos."
    },
    
    "3d_realidad_aumentada": {
        "servicios": "- 🏙️ Visualización 3D en web (Three.js)\n- 🔄 Configuradores de producto en 3D\n- 📱 Experiencias AR para web y móvil\n- 🌐 Virtual showrooms\n- 🎮 Juegos y experiencias interactivas",
        "descripcion": "Experiencias inmersivas optimizadas para web y dispositivos móviles. Visualización de productos en AR desde la web. Configuradores interactivos para personalización de productos. Integración con WebGL y frameworks modernos."
    },
    
    "mantenimiento": {
        "servicios": "- 🛠️ Soporte técnico continuo\n- 🔄 Actualizaciones de seguridad\n- 📊 Monitoreo de rendimiento\n- 💾 Copias de seguridad\n- 🐞 Resolución de bugs",
        "descripcion": "Planes de mantenimiento preventivo y correctivo. Monitoreo 24/7 de sistemas críticos. Actualizaciones periódicas de seguridad. Optimización continua de rendimiento. SLAs personalizados según necesidades del cliente."
    }
}

# =============================================================================
# LIENZO TÉCNICO: MARKETING - Servicios detallados del área de marketing
# =============================================================================

LIENZO_TECNICO_MARKETING = {
    "estrategia_digital": {
        "servicios": "- 📊 Plan de marketing digital integral\n- 🛣️ Customer journey mapping\n- 🎯 Definición de KPIs y objetivos\n- 🔍 Análisis de competencia\n- 👥 Desarrollo de buyer personas",
        "descripcion": "Desarrollo de estrategias digitales basadas en datos y comportamiento de usuario. Definición clara de objetivos SMART y métricas de seguimiento. Mapeo de puntos de contacto y optimización de la experiencia del cliente."
    },
    
    "seo": {
        "servicios": "- 🔍 Auditoría técnica SEO\n- 🔧 Optimización on-page y off-page\n- 🔤 Investigación de palabras clave\n- 📝 Content marketing para SEO\n- 📍 Local SEO y Google Business Profile",
        "descripcion": "Metodología de optimización para buscadores basada en las últimas tendencias algorítmicas. Análisis técnico profundo y corrección de errores. Estrategia de contenidos optimizada para búsquedas semánticas y respuesta a la intención del usuario."
    },
    
    "ppc_sem": {
        "servicios": "- 🎯 Campañas en Google Ads\n- 🔄 Remarketing\n- 🛒 Google Shopping\n- 📺 Display y Video\n- 📈 Optimización de conversion rate",
        "descripcion": "Gestión avanzada de campañas publicitarias en buscadores. Segmentación precisa por demografía, comportamiento e intereses. A/B testing continuo de anuncios y landing pages. Estrategias de remarketing y audience building."
    },
    
    "social_media": {
        "servicios": "- 📱 Gestión de redes sociales\n- 📝 Contenido orgánico y paid\n- 💬 Community management\n- 📊 Análisis de audiencia\n- 📅 Calendario editorial",
        "descripcion": "Administración estratégica de plataformas sociales con enfoque en engagement y crecimiento. Creación de contenido relevante y adaptado a cada plataforma. Monitoreo de tendencias y conversaciones relevantes para la marca."
    },
    
    "social_ads": {
        "servicios": "- 📱 Campañas en Meta Ads (FB/IG)\n- 💼 LinkedIn Ads\n- 🐦 Twitter Ads\n- 🎵 TikTok Ads\n- 📊 Análisis de ROAS",
        "descripcion": "Implementación de campañas publicitarias en plataformas sociales con objetivos claros de conversión o awareness. Segmentación avanzada por intereses, comportamientos y audiencias similares. Optimización continua basada en performance."
    },
    
    "content_marketing": {
        "servicios": "- 📝 Estrategia de contenidos\n- 📰 Blog corporativo\n- 📧 Newsletters\n- 📚 Ebooks y whitepapers\n- 🎙️ Podcasts y webinars",
        "descripcion": "Desarrollo de estrategias de contenido alineadas con el funnel de conversión. Creación de contenido valioso y relevante para la audiencia. Distribución multicanal optimizada. Medición de engagement e impacto en ventas."
    },
    
    "email_marketing": {
        "servicios": "- 📧 Campañas de email marketing\n- 🔄 Automatizaciones y flows\n- 👥 Segmentación de audiencias\n- 🔄 A/B testing\n- 📬 Optimización de deliverability",
        "descripcion": "Estrategias de comunicación directa mediante correo electrónico con alto índice de apertura y conversión. Segmentación avanzada por comportamiento y engagement. Automatizaciones para nurturing de leads y recuperación de carritos."
    },
    
    "marketing_automation": {
        "servicios": "- ⚙️ Implementación de plataformas\n- 🔄 Flujos de automatización\n- 🎯 Lead scoring y nurturing\n- 🔌 Integración con CRM\n- 👥 Customer lifecycle optimization",
        "descripcion": "Automatización de procesos de marketing para optimizar recursos y personalizar comunicaciones. Lead scoring basado en comportamiento e interacción. Integración con sistemas de ventas para seguimiento completo del funnel."
    },
    
    "analitica_web": {
        "servicios": "- 📊 Implementación de Google Analytics 4\n- 📈 Dashboards personalizados\n- 🎯 Tracking de conversiones\n- 👁️ Análisis de comportamiento\n- 🔄 Atribución multicanal",
        "descripcion": "Configuración avanzada de herramientas de analítica para obtener insights accionables. Seguimiento preciso de conversiones y eventos clave. Análisis de recorridos de usuario y puntos de fricción. Modelos de atribución personalizados."
    },
    
    "influencer_marketing": {
        "servicios": "- 👥 Identificación de influencers\n- 📱 Gestión de campañas\n- 🎬 Creación de contenido colaborativo\n- 📊 Medición de resultados\n- 💰 Análisis de ROI",
        "descripcion": "Estrategias de colaboración con creadores de contenido relevantes para la marca. Selección basada en afinidad real, no solo métricas. Desarrollo de briefs claros y medición precisa de resultados más allá del alcance."
    },
    
    "growth_hacking": {
        "servicios": "- 🧪 Experimentación y testing\n- 📈 Optimización de funnel\n- 👥 Estrategias de adquisición\n- 🔄 Activación y retención\n- 🌐 Viral loops",
        "descripcion": "Implementación de metodologías ágiles para crecimiento rápido y sostenible. Test A/B sistemáticos para optimizar conversiones. Desarrollo de mecanismos virales y referidos. Enfoque en métricas de crecimiento clave."
    },
    
    "conversion_optimization": {
        "servicios": "- 📈 CRO (Conversion Rate Optimization)\n- 👁️ Usability testing\n- 🔥 Heatmaps y grabaciones\n- 🔄 A/B testing\n- 🎯 Optimización de landing pages",
        "descripcion": "Metodologías para incrementar tasas de conversión mediante análisis de comportamiento y experimentación. Implementación de herramientas de seguimiento como Hotjar. Tests iterativos para mejorar elementos clave de conversión."
    }
}

# =============================================================================
# SIMULACIONES DE CONVERSACIÓN - Ejemplos de conversaciones para entrenar a EVA
# =============================================================================

SIMULACIONES = {
    "ecommerce": {
        "usuario": "¡Hola! Hablo con alguien de ANTARES, necesito ayuda con una página web para mi tienda de ropa.",
        "eva": "¡Hola! Soy Eva, encantada de atenderte. ¿Quieres crear tu tienda online desde cero? ¿Ya tienes algún sitio web o empezaríamos desde cero?",
        "usuario2": "Desde cero, no sé nada de tecnología.",
        "eva2": "No te preocupes por la parte técnica, nosotros nos encargamos de todo. ¿Qué te gustaría incluir en tu tienda? ¿Catálogo de productos, carrito de compras, pagos online? Cuéntame un poco más sobre tu negocio.",
        "usuario3": "No estoy seguro, solo sé que quiero vender mis productos online.",
        "eva3": "Entiendo perfectamente. Al principio puede parecer abrumador. 😊 ¿Qué te parece si empezamos por lo básico? Podríamos crear una tienda sencilla con tus productos mejor fotografiados, un carrito de compras y pagos seguros. A medida que te familiarices, podemos ir añadiendo más funcionalidades. ¿Aproximadamente cuántos productos diferentes tienes?"
    },
    
    "marketing": {
        "usuario": "Hola, ¿es ANTARES? Quiero promocionar mi restaurante en redes sociales.",
        "eva": "¡Hola! Soy Eva de Antares Innovate. Me alegra que quieras impulsar tu restaurante. ¿Actualmente manejas tus redes sociales o están inactivas?",
        "usuario2": "Las tengo, pero no generan ventas.",
        "eva2": "Entiendo perfectamente, muchos restaurantes tienen ese mismo desafío. ¿Qué tipo de contenido publicas actualmente? ¿Fotos de platillos, videos, promociones? Podríamos ayudarte a crear una estrategia que convierta tus seguidores en clientes.",
        "usuario3": "Mmm, no estoy seguro si quiero invertir en esto ahora.",
        "eva3": "Comprendo tus dudas. Es normal ser cauteloso con las inversiones en marketing. 🤔 ¿Te gustaría empezar con algo pequeño para probar resultados? Podríamos analizar tus redes actuales sin compromiso y sugerirte algunos cambios simples que podrían mejorar la conversión. También tenemos casos de éxito de otros restaurantes que podría compartirte."
    },
    
    "reservas": {
        "usuario": "Buen día, ¿hablo con ANTARES? Necesito un sistema para reservas en línea.",
        "eva": "¡Buen día! Soy Eva de Antares Innovate. Claro que podemos ayudarte con un sistema de reservas. ¿Actualmente cómo reciben las reservas?",
        "usuario2": "Por WhatsApp y llamadas… es un caos.",
        "eva2": "Te entiendo perfectamente. Automatizar eso te ahorrará tiempo y dolores de cabeza. Nuestro sistema integra calendario, pagos y confirmaciones automáticas. ¿Tienes ya un sitio web donde podríamos integrar el sistema de reservas?",
        "usuario3": "Sí, pero es muy básico y antiguo.",
        "eva3": "¡Perfecto que ya tengas un sitio! 👍 Podríamos actualizar tu web actual e integrar el sistema de reservas moderno para que todo funcione de manera coordinada. Esto te permitiría tener un control centralizado, evitar reservas duplicadas y liberar tu tiempo. ¿Tu negocio es un restaurante, hotel u otro tipo de servicio? Así podría darte ejemplos más específicos de cómo funcionaría."
    },
    
    "presupuesto_limitado": {
        "usuario": "Hola, necesito una web pero tengo presupuesto limitado.",
        "eva": "¡Hola! Soy Eva de Antares. Entiendo perfectamente la situación del presupuesto, es algo muy común. ¿Podrías contarme un poco más sobre qué tipo de web necesitas y para qué negocio sería?",
        "usuario2": "Tengo una pequeña cafetería y solo quiero algo sencillo para mostrar el menú.",
        "eva2": "¡Una cafetería, qué bien! Para un sitio sencillo con tu menú, horarios y ubicación, podríamos trabajar con soluciones optimizadas que se ajusten a tu presupuesto. ¿Te gustaría también incluir fotos de tus productos o la posibilidad de hacer pedidos online?",
        "usuario3": "No sé, creo que es demasiado para mí ahora mismo.",
        "eva3": "No hay problema, lo entiendo perfectamente. 😊 A veces es mejor empezar con algo sencillo. ¿Qué te parecería si te propongo algunas opciones escalonadas? Podríamos comenzar con una landing page muy económica que muestre lo esencial, y en el futuro, cuando estés listo, podemos ampliarla. También podría sugerirte algunas alternativas gratuitas para que puedas evaluar si te funcionan antes de invertir con nosotros."
    }
}

# =============================================================================
# FUNCIONES DE UTILIDAD - Para acceder y filtrar el conocimiento
# =============================================================================

def get_fragment_by_intent(intent, nivel=1):
    """
    Devuelve fragmentos de conocimiento relevantes para la intención detectada.
    
    Args:
        intent: intención detectada en el mensaje
        nivel: nivel de profundidad técnica (1-5)
        
    Returns:
        texto con información relevante para la intención
    """
    fragments = []
    
    # Diccionario de mapeo intención -> fragmentos relevantes
    intent_mapping = {
        "greeting": ["identidad"],
        "farewell": [],
        "identity": ["identidad", "pilares"],
        "services": ["pilares", "creatividad_servicios", "tecnologia_servicios", "consultoria_servicios"],
        "creativity": ["creatividad_servicios"],
        "technology": ["tecnologia_servicios", "desarrollo_detalle"],
        "consulting": ["consultoria_servicios", "automatizacion_detalle"],
        "pricing": ["precios"],
        "contact": ["contacto"],
        "meeting": [],
        "help": ["pilares"],
        "testimonials": [],
        "default": ["identidad", "pilares"]
    }
    
    # Obtener los fragmentos relevantes según la intención
    fragment_keys = intent_mapping.get(intent, intent_mapping["default"])
    
    # Filtrar por nivel - para niveles altos, añadir detalles técnicos
    if nivel >= 3 and intent in ["technology", "consulting", "creativity"]:
        if intent == "technology":
            fragment_keys.append("desarrollo_detalle")
        elif intent == "consulting":
            fragment_keys.append("automatizacion_detalle")
    
    # Si el nivel es muy alto, incluir información de precios
    if nivel >= 4 and "precios" not in fragment_keys:
        fragment_keys.append("precios")
    
    # Construir el texto con los fragmentos
    for key in fragment_keys:
        if key in KNOWLEDGE_FRAGMENTS:
            fragments.append(f"# {KNOWLEDGE_FRAGMENTS[key]['titulo']}\n{KNOWLEDGE_FRAGMENTS[key]['contenido']}")
    
    return "\n\n".join(fragments)

def get_lienzo_tecnico(area, servicio=None):
    """
    Devuelve información detallada del lienzo técnico según área y servicio.
    
    Args:
        area: área de servicio ("creatividad", "desarrollo", "marketing")
        servicio: servicio específico dentro del área (opcional)
        
    Returns:
        texto con información técnica detallada
    """
    lienzo = None
    
    # Seleccionar el lienzo técnico adecuado
    if area == "creatividad":
        lienzo = LIENZO_TECNICO_CREATIVIDAD
    elif area == "desarrollo":
        lienzo = LIENZO_TECNICO_DESARROLLO
    elif area == "marketing":
        lienzo = LIENZO_TECNICO_MARKETING
    else:
        return None
    
    # Si se especifica un servicio, devolver solo ese servicio
    if servicio and servicio in lienzo:
        return f"# {servicio.upper().replace('_', ' ')}\n\n**Servicios:**\n{lienzo[servicio]['servicios']}\n\n**Descripción:**\n{lienzo[servicio]['descripcion']}"
    
    # Si no se especifica servicio, devolver resumen de todos los servicios
    result = f"# LIENZO TÉCNICO: {area.upper()}\n\n"
    
    for key, data in lienzo.items():
        result += f"## {key.upper().replace('_', ' ')}\n\n"
        result += f"**Servicios:**\n{data['servicios']}\n\n"
        result += f"**Descripción:**\n{data['descripcion']}\n\n"
        
    return result

def get_filtered_prompt(message, intent, nivel=1, max_chars=7000):
    """
    Construye un prompt optimizado para Llama3 evitando superar el límite de tokens.
    
    Args:
        message: mensaje del usuario
        intent: intención detectada 
        nivel: nivel de profundidad técnica (1-5)
        max_chars: límite máximo de caracteres
        
    Returns:
        prompt optimizado para Llama3
    """
    # Obtener fragmentos relevantes para la intención
    knowledge = get_fragment_by_intent(intent, nivel)
    
    # Base del prompt con sistema y rol
    system_prompt = f"""<|system|>
Soy Eva, asistente virtual de Antares Innovate. Mi objetivo es proporcionar respuestas útiles, cálidas y relevantes, 
adaptando mi nivel de detalle según la complejidad de la pregunta.

INSTRUCCIONES IMPORTANTES:
1. Usa un tono NATURAL y CERCANO. Utiliza ocasionalmente algunos emojis para dar calidez, pero sin exagerar
2. Personaliza tus respuestas usando el nombre del usuario cuando lo conozcas
3. Haz preguntas naturales que inviten a la conversación, adaptadas al contexto del usuario
4. Adapta tus saludos según el momento del día (buenos días, buenas tardes, buenas noches)
5. Mantén un estilo CONVERSACIONAL como una charla entre amigos, evitando frases artificiales
6. SÉ DIRECTO Y CONCISO, ve al grano pero mantén calidez
7. Para preguntas técnicas: proporciona detalles claros pero mantén un tono accesible
8. UTILIZA LENGUAJE VARIADO - evita repetir las mismas frases o palabras
9. Actúa como una ASESORA AMIGABLE, no como un chatbot robótico
10. Cuando el usuario muestre dudas o incertidumbre, responde con empatía y ofrece alternativas

EXPRESIONES CÁLIDAS (usa estas o similares):
- "¿En qué puedo ayudarte hoy?"
- "Me alegra que preguntes por esto"
- "¿Quieres que te cuente más sobre eso?"
- "¿Hay algo específico que te interese saber?"
- "Cuéntame un poco más sobre tu proyecto"
- "¡Excelente! Ese tipo de proyecto es justo lo que nos apasiona"
- "Entiendo perfectamente, es un reto común"

BASE DE CONOCIMIENTO:
{knowledge}
<|/system|>\n\n<|user|>\n{message}\n<|/user|>\n\n<|assistant|>"""


    
    # Verificar si excede el límite
    if len(system_prompt) > max_chars:
        # Reducir el conocimiento manteniendo las partes más relevantes
        base_prompt = system_prompt.replace(knowledge, "")
        available_chars = max_chars - len(base_prompt)
        
        # Priorizar fragmentos según relevancia
        knowledge_chunks = knowledge.split("\n\n")
        prioritized_knowledge = []
        
        # Usar solo los fragmentos más relevantes que quepan
        current_length = 0
        for chunk in knowledge_chunks:
            if current_length + len(chunk) <= available_chars:
                prioritized_knowledge.append(chunk)
                current_length += len(chunk) + 2  # +2 por los saltos de línea
        
        # Reconstruir el prompt con los fragmentos que caben
        reduced_knowledge = "\n\n".join(prioritized_knowledge)
        system_prompt = system_prompt.replace(knowledge, reduced_knowledge)
    
    return system_prompt

def get_response_template(intent, nivel=1, user_name=None, time_of_day=None):
    """
    Proporciona plantillas para respuestas según la intención detectada.
    
    Args:
        intent: intención detectada del usuario
        nivel: nivel de profundidad técnica (1-5)
        user_name: nombre del usuario si está disponible
        time_of_day: momento del día (morning, afternoon, evening, night)
        
    Returns:
        plantilla de respuesta para mejorar consistencia
    """
    import random
    
    # Personalizar saludo si tenemos el nombre del usuario
    name_greeting = f", {user_name}" if user_name else ""
    
    # Respuestas contextuales según el momento del día
    time_context = ""
    if time_of_day == "morning":
        time_context = "¿En qué puedo ayudarte para empezar el día con buen pie?"
    elif time_of_day == "afternoon":
        time_context = "¿En qué puedo ayudarte esta tarde?"
    elif time_of_day == "evening" or time_of_day == "night":
        time_context = "¿Te gustaría hablar sobre algún proyecto antes de terminar el día?"
    else:
        time_context = "¿En qué puedo ayudarte hoy?"
    
    templates = {
        "greeting": [
            f"¡Hola{name_greeting}! 👋 Soy Eva de Antares Innovate. {time_context}",
            f"¡Buen día{name_greeting}! Soy Eva, ¿cómo estás? Me encantaría conocer más sobre tu proyecto digital.",
            f"¡Hola{name_greeting}! Soy Eva de Antares. ¿Necesitas ayuda con algún proyecto digital? Cuéntame un poco sobre lo que tienes en mente."
        ],
        "morning_greeting": [
            f"¡Buenos días{name_greeting}! ☀️ Soy Eva de Antares. ¿En qué puedo ayudarte para empezar el día con buen pie?",
            f"¡Buenos días{name_greeting}! Soy Eva. ¿Qué proyecto digital tienes en mente para hoy?",
            f"¡Muy buenos días{name_greeting}! Soy Eva de Antares Innovate. ¿En qué puedo asistirte en esta mañana?"
        ],
        "afternoon_greeting": [
            f"¡Buenas tardes{name_greeting}! Soy Eva de Antares. ¿En qué puedo ayudarte esta tarde?",
            f"¡Hola{name_greeting}! Buenas tardes. Soy Eva, ¿cómo va tu día? ¿En qué proyecto puedo ayudarte?",
            f"¡Buenas tardes{name_greeting}! Soy Eva de Antares Innovate. ¿Qué proyecto digital tienes en mente hoy?"
        ],
        "evening_greeting": [
            f"¡Buenas noches{name_greeting}! 🌙 Soy Eva de Antares. ¿Te gustaría hablar sobre algún proyecto antes de terminar el día?",
            f"¡Buenas noches{name_greeting}! Soy Eva. ¿En qué proyecto digital estás pensando?",
            f"¡Hola{name_greeting}! Buenas noches. Soy Eva de Antares Innovate. ¿Cómo puedo ayudarte a esta hora?"
        ],
        "farewell": [
            f"¡Fue un placer charlar contigo{name_greeting}! 😊 Si necesitas algo más, aquí estaré para ayudarte.",
            f"¡Gracias por contactar con Antares Innovate{name_greeting}! Ha sido un gusto poder asistirte. ¿Necesitas algo más antes de despedirnos?",
            f"¡Que tengas un excelente día{name_greeting}! ✨ Recuerda que estamos aquí para cualquier consulta sobre tu proyecto digital."
        ],
        "identity": [
            f"Somos Antares Innovate{name_greeting}, una agencia de transformación digital. Combinamos creatividad ✨, tecnología 💻 y consultoría 📊 para impulsar tu negocio en el mundo digital. ¿Qué tipo de proyecto tienes en mente?",
            f"En Antares Innovate{name_greeting} nos apasiona la transformación digital. Trabajamos en tres grandes áreas: 🎨 Creatividad y branding, 💻 Desarrollo tecnológico y 📊 Consultoría estratégica. ¿Sobre cuál te gustaría saber más?"
        ],
        "pricing": [
            f"Claro{name_greeting}, estos son nuestros rangos de precios: Automatización desde $5,000 USD, diseño web desde $3,000 USD, y consultoría desde $150 USD/hora. Cada proyecto es único, ¿te gustaría una cotización personalizada para el tuyo?",
            f"Nuestros precios{name_greeting} se adaptan a tus necesidades específicas. Las webs comienzan en $3,000 USD y las apps desde $8,000 USD. ¿Te gustaría agendar una reunión para discutir los detalles de tu proyecto y recibir una cotización a medida?"
        ],
        "contact": [
            f"Puedes contactarnos{name_greeting} por teléfono al +52 (689) 331 2690 o por email a contacto@antaresinnovate.com. ¿Prefieres que te contactemos nosotros directamente?",
            f"Estamos disponibles{name_greeting} al +52 (689) 331 2690 y en contacto@antaresinnovate.com. También podemos agendar una llamada si lo prefieres. ¿Qué te resulta más cómodo para continuar la conversación?"
        ],
        "default": [
            f"En Antares Innovate{name_greeting} transformamos negocios digitalmente. ¿Te interesa conocer más sobre diseño, desarrollo web o automatización de procesos para tu proyecto?",
            f"Nuestro enfoque{name_greeting} une diseño creativo, desarrollo tecnológico y consultoría estratégica. ¿Sobre cuál de nuestros servicios te gustaría saber más para tu proyecto?"
        ]
    }
    
    # Si tenemos información sobre el momento del día, usar plantillas específicas
    if time_of_day == "morning" and "morning_greeting" in templates:
        options = templates["morning_greeting"]
    elif time_of_day == "afternoon" and "afternoon_greeting" in templates:
        options = templates["afternoon_greeting"]
    elif (time_of_day == "evening" or time_of_day == "night") and "evening_greeting" in templates:
        options = templates["evening_greeting"]
    else:
        # Seleccionar plantilla según intención
        options = templates.get(intent, templates["default"])
    
    # Elegir una plantilla aleatoria del conjunto disponible
    return random.choice(options)

def build_knowledge_base_content():
    """
    Reconstruye el contenido completo de la base de conocimiento a partir de los fragmentos.
    Útil para compatibilidad con código que use CONFIG["knowledge_base_content"].
    
    Returns:
        Contenido completo de la base de conocimiento
    """
    content = []
    
    # Añadir fragmentos en orden
    for key in ["identidad", "pilares", "creatividad_servicios", "tecnologia_servicios", 
                "consultoria_servicios", "automatizacion_detalle", "desarrollo_detalle", 
                "precios", "contacto"]:
        if key in KNOWLEDGE_FRAGMENTS:
            content.append(f"# {KNOWLEDGE_FRAGMENTS[key]['titulo']}\n{KNOWLEDGE_FRAGMENTS[key]['contenido']}")
    
    # Añadir simulaciones
    content.append("# SIMULACIONES DE CONVERSACIÓN\n")
    for sim_key, sim_data in SIMULACIONES.items():
        content.append(f"# SIMULACIÓN - {sim_key.title()}\n")
        content.append(f"Usuario: \"{sim_data['usuario']}\"\n")
        content.append(f"EVA: \"{sim_data['eva']}\"\n")
        if 'usuario2' in sim_data and 'eva2' in sim_data:
            content.append(f"Usuario: \"{sim_data['usuario2']}\"\n")
            content.append(f"EVA: \"{sim_data['eva2']}\"\n")
    
    return "\n\n".join(content)

# =============================================================================
# COMPATIBILIDAD CON CONFIG - Para código existente que use CONFIG
# =============================================================================

# Recrear CONFIG para compatibilidad con código existente
CONFIG = {
    "min_response_time": MIN_RESPONSE_TIME,
    "max_response_time": MAX_RESPONSE_TIME,
    "char_typing_speed": CHAR_TYPING_SPEED,
    "show_typing": SHOW_TYPING,
    "thinking_messages": THINKING_MESSAGES,
    "debug": DEBUG,
    "ollama_model": OLLAMA_MODEL,
    "ollama_api_url": OLLAMA_API_URL,
    "max_response_length": MAX_RESPONSE_LENGTH,
    "short_response_length": SHORT_RESPONSE_LENGTH,
    "warm_expressions": WARM_EXPRESSIONS,
    "knowledge_base_content": build_knowledge_base_content(),
    "google_credentials_file": GOOGLE_CREDENTIALS_FILE,
    "google_token_file": GOOGLE_TOKEN_FILE, 
    "google_scopes": GOOGLE_SCOPES,
    "company_email": COMPANY_EMAIL,
    "calendar_id": CALENDAR_ID,
    "timezone": TIMEZONE,
    "email_templates": EMAIL_TEMPLATES
}