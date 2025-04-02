import requests
import json

OLLAMA_URL = "https://ollama-eva.onrender.com/api/generate"

payload = {
    "model": "llama3",
    "prompt": "¿Cuál es la capital de Francia?",
    "stream": False,
    "max_tokens": 100
}

print("[INFO] Enviando solicitud a Ollama...")

try:
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        print("[✅] Respuesta de Ollama:")
        print(data.get("response", "No hubo respuesta"))
    else:
        print(f"[❌] Error {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"[❌] Error al conectar: {e}")
