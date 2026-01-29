# 📦 Guía de Despliegue - INMO

## ⚠️ ANTES DE DESPLEGAR

### 1. Verificar que las API keys NO estén hardcodeadas
✅ Ya corregido - Las API keys ahora se leen desde variables de entorno

### 2. Configurar tus API keys reales

Edita el archivo `.env` en la raíz del proyecto:
```bash
OPENROUTER_API_KEY=tu_api_key_real_aqui
PROXYSCRAPE_API_KEY=tu_api_key_real_aqui  # Opcional
```

---

## 🚀 OPCIÓN 1: Despliegue con Vercel CLI (Recomendado)

### Paso 1: Instalar Vercel CLI
```bash
npm install -g vercel
```

### Paso 2: Login en Vercel
```bash
vercel login
```

### Paso 3: Desplegar el Frontend
Desde la raíz del proyecto:
```bash
vercel
```

Sigue las instrucciones:
- **Set up and deploy?** → Yes
- **Which scope?** → Selecciona tu cuenta
- **Link to existing project?** → No
- **Project name?** → inmo-paraguay (o el que prefieras)
- **Directory?** → `./frontend`
- **Override settings?** → No

### Paso 4: Configurar Variables de Entorno en Vercel

Opción A - Desde el CLI:
```bash
vercel env add NEXT_PUBLIC_API_URL
```
Valor: `https://tu-backend.onrender.com` (lo configuraremos después)

Opción B - Desde el Dashboard:
1. Ve a [vercel.com/dashboard](https://vercel.com/dashboard)
2. Selecciona tu proyecto
3. Settings → Environment Variables
4. Agrega: `NEXT_PUBLIC_API_URL` = `https://tu-backend.onrender.com`

### Paso 5: Redesplegar con las variables
```bash
vercel --prod
```

---

## 🐍 OPCIÓN 2: Desplegar Backend en Render.com

### Paso 1: Preparar el repositorio
1. Sube tu código a GitHub (asegúrate de que `.env` esté en `.gitignore`)
2. Verifica que `requirements.txt` esté en la raíz o en `/backend`

### Paso 2: Crear Web Service en Render
1. Ve a [render.com](https://render.com) y crea una cuenta
2. Click en **New +** → **Web Service**
3. Conecta tu repositorio de GitHub
4. Configura:

**Configuración Básica:**
- **Name**: `inmo-backend`
- **Region**: Oregon (US West) o el más cercano
- **Branch**: `main`
- **Root Directory**: `backend` (si tu backend está en una carpeta)
- **Runtime**: Python 3

**Build & Deploy:**
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

**Environment Variables:**
- Click en **Advanced** → **Add Environment Variable**
- Agrega:
  - `OPENROUTER_API_KEY` = `tu_api_key_real`
  - `PROXYSCRAPE_API_KEY` = `tu_api_key_real` (opcional)
  - `PYTHON_VERSION` = `3.11.0`

5. Click en **Create Web Service**

### Paso 3: Obtener la URL del Backend
Una vez desplegado, Render te dará una URL como:
```
https://inmo-backend-xxxx.onrender.com
```

### Paso 4: Actualizar Frontend
Actualiza la variable `NEXT_PUBLIC_API_URL` en Vercel con esta URL.

---

## 🔄 OPCIÓN 3: Despliegue con Git Integration (Automático)

### Configurar Vercel con GitHub
1. Ve a [vercel.com/new](https://vercel.com/new)
2. Importa tu repositorio de GitHub
3. Configura:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Agrega variables de entorno
5. Deploy

Cada push a `main` desplegará automáticamente.

---

## ✅ Verificación Post-Despliegue

### Frontend
1. Abre la URL de Vercel
2. Deberías ver la interfaz de INMO
3. Si hay error de conexión, verifica `NEXT_PUBLIC_API_URL`

### Backend
1. Abre `https://tu-backend.onrender.com`
2. Deberías ver:
```json
{
  "nombre": "INMO API",
  "version": "1.0.0",
  ...
}
```

### Integración
1. Envía un mensaje en el chat
2. Debería responder el agente
3. Si hay error 500, verifica que `OPENROUTER_API_KEY` esté configurada

---

## 🐛 Troubleshooting

### Error: "OPENROUTER_API_KEY no está configurada"
- Verifica que la variable esté en Render
- Reinicia el servicio en Render

### Error: "No puedo conectar con el servidor"
- Verifica que `NEXT_PUBLIC_API_URL` apunte al backend correcto
- Verifica que el backend esté corriendo (no en sleep mode)

### Error 403/CORS
- Actualiza `allow_origins` en `backend/main.py`:
```python
allow_origins=["*"]  # Para testing
# O específicamente:
allow_origins=["https://tu-frontend.vercel.app"]
```

---

## 💰 Costos

- **Vercel**: Free tier (100GB bandwidth, 6000 min build)
- **Render**: Free tier (750 horas/mes, sleep después de inactividad)
- **OpenRouter**: Según uso (Grok ~$0.50 por 1M tokens)

---

## 📞 Soporte

Si tienes problemas, contacta a [@guaraniux](https://t.me/guaraniux)
