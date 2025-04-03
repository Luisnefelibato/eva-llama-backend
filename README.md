# EVA + Ollama + LocalTunnel

## ✨ Objetivo
Configurar un entorno local donde EVA (agente conversacional) utilice el modelo LLaMA 3 servido por Ollama y se exponga vía LocalTunnel para poder ser consumido desde un backend desplegado en Render.

---

## ✅ Requisitos

- [x] Tener instalado [Ollama](https://ollama.com/)
- [x] Tener `node` y `npm` instalados
- [x] Tener `git`
- [x] Tener `eva_llama_14.py` configurado
- [x] Conexión a GitHub (deploy en Render)

---

## 🚀 Paso a paso

### 1. Iniciar el servidor de Ollama

```bash
set OLLAMA_HOST=0.0.0.0  # En Windows CMD
ollama serve
```

Esto hace que Ollama acepte conexiones externas (necesario para LocalTunnel).

---

### 2. Instalar LocalTunnel (una vez)

```bash
npm install -g localtunnel
```

Si no tenés permisos, podés usar `npx localtunnel` directamente.

---

### 3. Crear el túnel y obtener la URL

```bash
lt --port 11434
```

Obtendrás una URL como:

```
https://shiny-penguin.loca.lt
```

---

### 4. Actualizar `eva_llama_14.py`

Buscá la parte donde se define la URL de Ollama:

```python
CONFIG["ollama_api_url"] = "https://anterior-url.loca.lt/api/generate"
```

Y reemplazala por la nueva URL:

```python
CONFIG["ollama_api_url"] = "https://shiny-penguin.loca.lt/api/generate"
```

---

### 5. Subir los cambios a GitHub

```bash
git add eva_llama_14.py
git commit -m "Actualizar URL de Ollama"
git push origin main
```

Render hará el redeploy automáticamente y EVA usará la nueva instancia de Ollama.

---

## 🤖 Automatizar el flujo

Crea un archivo `actualizar_ollama_url.sh`:

```bash
#!/bin/bash

export OLLAMA_HOST=0.0.0.0
ollama serve &

sleep 3

url=$(npx localtunnel --port 11434 | grep -Eo "https://[a-zA-Z0-9\-]+\.loca\.lt")

sed -i '' "s|https://.*\.loca\.lt/api/generate|$url/api/generate|g" eva_llama_14.py

git add eva_llama_14.py
git commit -m "Actualizar URL del túnel Ollama"
git push origin main

echo "[✅] Nuevo URL aplicado: $url"
```

Hacelo ejecutable:

```bash
chmod +x actualizar_ollama_url.sh
```

Ejecutalo cuando quieras actualizar el túnel:

```bash
./actualizar_ollama_url.sh
```

---

## 🧪 Prueba en Postman

**Endpoint EVA (Render):**
```
https://eva-llama-backend.onrender.com/chat
```

**Body:**
```json
{
  "message": "Hola EVA, ¿qué podés hacer?"
}
```

**Header:**
```
Content-Type: application/json
```

---

## ✅ Resultado

Tu backend EVA estará vinculado dinámicamente con Ollama local, incluso cuando LocalTunnel reinicie su URL.

