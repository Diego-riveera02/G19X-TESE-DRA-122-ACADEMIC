# PluriOne: Plataforma de Observabilidad de Datos con IA

**PluriOne** es una plataforma diseñada para monitorear, detectar y diagnosticar anomalías en flujos de datos corporativos en tiempo real, utilizando inteligencia artificial (J.A.R.V.I.S.) para emitir recomendaciones técnicas.

## 📋 Requisitos Previos
- Python 3.10 o superior
- Node.js 18 o superior
- PostgreSQL
- Docker (opcional)

## ⚙️ Variables de Entorno
Crea un archivo `.env` dentro de la carpeta `backend/` copiando el contenido de `.env.example`:
- `DATABASE_URL`: Conexión a tu base de datos PostgreSQL.
- `SENDER_EMAIL` y `SENDER_PASSWORD`: Credenciales para correos.
- `SECRET_KEY`: Llave de seguridad para los tokens JWT.
- `GROQ_API_KEY`: Tu llave de acceso para la Inteligencia Artificial.

## 🚀 Cómo levantarlo SIN Docker

**1. Backend:**
Ingresa a la carpeta `backend/`, activa tu entorno virtual, instala dependencias (`pip install -r requirements.txt`) y ejecuta:
`uvicorn app.main:app --reload`

**2. Frontend:**
Ingresa a la carpeta `frontend/`, instala los paquetes (`npm install`) y ejecuta:
`npm run dev`

## 🐳 Cómo levantarlo CON Docker
En la raíz del proyecto (donde está el archivo `docker-compose.yml`), abre tu terminal y ejecuta:
`docker-compose up --build`