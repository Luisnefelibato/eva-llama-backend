#!/bin/bash

# Script: actualizar_ollama_url.sh
# Automatiza:
# 1. Lanzar ollama serve con OLLAMA_HOST=0.0.0.0
# 2. Iniciar un túnel con localtunnel
# 3. Obtener URL del túnel
# 4. Reemplazar la URL en eva_llama_14.py
# 5. Hacer commit y push a GitHub

# --- CONFIGURACIÓN ---
MODEL_NAME="llama3"
ARCHIVO_EVA="eva_llama_14.py"

# --- INICIAR OLLAMA ---
echo "[🧠] Iniciando servidor Ollama en background..."
export OLLAMA_HOST=0.0.0.0
ollama serve &
OLLAMA_PID=$!

# Esperar unos segundos para que arranque
sleep 5

# --- CREAR TÚNEL ---
echo "[🌐] Creando túnel con LocalTunnel..."
url=$(npx localtunnel --port 11434 | grep -Eo "https://[a-zA-Z0-9\-]+\.loca\.lt")

if [[ -z "$url" ]]; then
  echo "[❌] Error: No se pudo obtener URL del túnel."
  kill $OLLAMA_PID
  exit 1
fi

# --- ACTUALIZAR URL EN CÓDIGO ---
echo "[✏️] Reemplazando URL anterior en $ARCHIVO_EVA..."
sed -i '' "s|https://.*\.loca\.lt/api/generate|$url/api/generate|g" "$ARCHIVO_EVA"

# --- PUSH A GITHUB ---
echo "[📤] Subiendo cambios al repositorio..."
git add "$ARCHIVO_EVA"
git commit -m "Actualizar URL de túnel Ollama a $url"
git push origin main

# --- FINAL ---
echo "[✅] Nuevo túnel activo: $url"
echo "[🚀] EVA se redeplegará en Render con la nueva URL."
echo "[🔁] Ollama sigue corriendo en background (PID: $OLLAMA_PID)"
