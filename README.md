# INMO - Asistente Inmobiliario Paraguay

Asistente conversacional inteligente para búsqueda de propiedades inmobiliarias en Paraguay.

## 🏗️ Arquitectura

- **Frontend**: Next.js 14 + React + TypeScript + TailwindCSS
- **Backend**: FastAPI + Python
- **Scraper**: InfoCasas Paraguay
- **IA**: OpenRouter (Grok 4.1)

## 📋 Requisitos

### Backend
- Python 3.8+
- Variables de entorno requeridas:
  - `OPENROUTER_API_KEY` (requerida)
  - `PROXYSCRAPE_API_KEY` (opcional, para proxies)

### Frontend
- Node.js 18+
- Variables de entorno:
  - `NEXT_PUBLIC_API_URL` (URL del backend)

## 🚀 Despliegue

### Frontend (Vercel)

1. Instalar Vercel CLI:
```bash
npm install -g vercel
```

2. Desplegar desde la raíz del proyecto:
```bash
vercel
```

3. Configurar variables de entorno en Vercel:
   - `NEXT_PUBLIC_API_URL`: URL de tu backend desplegado

### Backend (Render.com)

1. Crear cuenta en [Render.com](https://render.com)
2. Crear nuevo Web Service
3. Conectar repositorio de GitHub
4. Configurar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `OPENROUTER_API_KEY`: Tu API key de OpenRouter
     - `PROXYSCRAPE_API_KEY`: Tu API key de ProxyScrape (opcional)

## 🔒 Seguridad

- ✅ API keys eliminadas del código
- ✅ Variables de entorno configuradas
- ✅ `.gitignore` protege archivos sensibles
- ⚠️ **IMPORTANTE**: Nunca subas el archivo `.env` a Git

## 💻 Desarrollo Local

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📝 Notas

- El frontend se conecta al backend mediante `NEXT_PUBLIC_API_URL`
- El scraper funciona sin proxies si `PROXYSCRAPE_API_KEY` no está configurada
- El agente requiere `OPENROUTER_API_KEY` para funcionar

## 👤 Autor

Guaraniux - [@guaraniux](https://t.me/guaraniux)
