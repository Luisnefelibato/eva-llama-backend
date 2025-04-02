#!/bin/bash

# Ruta del log para guardar salida del servidor
LOGFILE="$HOME/ollama_server.log"

# Iniciar Ollama en segundo plano y registrar log
echo "[INFO] Iniciando Ollama..." >> "$LOGFILE"
ollama serve >> "$LOGFILE" 2>&1 &

# Esperar unos segundos a que Ollama arranque
sleep 5

# Verificar si el modelo llama3:8b está presente
if ! ollama list | grep -q "llama3:8b"; then
  echo "[INFO] Modelo llama3:8b no encontrado. Descargando..." >> "$LOGFILE"
  ollama pull llama3:8b >> "$LOGFILE" 2>&1
else
  echo "[INFO] Modelo llama3:8b ya está instalado." >> "$LOGFILE"
fi

echo "[INFO] Ollama listo y corriendo." >> "$LOGFILE"
