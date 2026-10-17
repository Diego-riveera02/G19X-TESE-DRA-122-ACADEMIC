PluriOne — Plataforma de Observabilidad de Datos con Inteligencia Artificial
PluriOne es un prototipo académico funcional de observabilidad de datos. Permite visualizar métricas de pipelines, registrar anomalías, consultar su historial y obtener explicaciones técnicas mediante el asistente conversacional J.A.R.V.I.S., integrado con Groq.
Alcance actual: la telemetría procede de un simulador interno del backend. Las métricas no se capturan de infraestructura empresarial real. Las causas propuestas por la IA son hipótesis para investigar, no incidentes ni causas raíz comprobados.

1. Funcionalidades implementadas
- Telemetría automática simulada: un proceso asíncrono en FastAPI genera registros de prueba aproximadamente cada 5 segundos, sin botones de inyección manual.
- Persistencia: PostgreSQL almacena usuarios y anomalías con identificador, pipeline, métrica, valor, estado, recomendación y fecha de registro.
- Monitoreo en tiempo real: React presenta gráficas de latencia, calidad de datos y fallos, junto con un feed de alertas. WebSocket entrega eventos a las sesiones autenticadas del usuario correspondiente.
- Acceso a la plataforma: registro, verificación de cuenta mediante código enviado por correo, inicio de sesión con JWT, contraseñas almacenadas mediante hash y flujo de recuperación de contraseña con código.
- J.A.R.V.I.S. 2.0: chat en español mediante Groq, seguimiento del contexto reciente de la conversación y consultas autorizadas a PostgreSQL mediante function calling.
- Consultas de anomalías: la herramienta disponible permite consultar el total y hasta 10 registros recientes del usuario autenticado, filtrados por estado normal, alerta, critico o todos. No se incluyen todavía filtros por fecha, métrica o severidad.
- Diagnósticos orientativos: J.A.R.V.I.S. relaciona los datos consultados con posibles causas y acciones de investigación. No confirma causas sin evidencia adicional ni ejecuta cambios en sistemas externos.
- Interfaz del asistente: renderizado Markdown con tablas, desplazamiento horizontal dentro de tablas extensas, desplazamiento vertical de la conversación y botón «↓ Último».
- Historial y reportes: visualización de anomalías y exportación a PDF de los registros cargados en la interfaz; guía de bienvenida (onboarding).
Aclaración sobre las recomendaciones automáticas: la telemetría del simulador utiliza diagnósticos o recomendaciones locales predefinidas. Groq se utiliza para el asistente conversacional; no se realiza una llamada al modelo por cada métrica generada.
2. Tecnologías
Componente	Tecnología
Backend y API	Python, FastAPI, SQLAlchemy
Base de datos	PostgreSQL
Interfaz	React, Vite, React Router, Axios
Gráficas	Recharts
Actualizaciones	WebSockets autenticados con JWT
Asistente	Groq API, modelo openai/gpt-oss-20b, herramientas de consulta controladas por el backend
Respuestas enriquecidas	react-markdown, remark-gfm
Reportes	jsPDF y jspdf-autotable
Entorno local	Docker Compose para los servicios configurados; Vite para el frontend


3. Requisitos previos
- Git, si se trabaja desde el repositorio.
- Docker y Docker Compose para levantar los servicios de backend y PostgreSQL en el entorno utilizado en las pruebas.
- Node.js y npm en una versión compatible con Vite (consultar frontend/package.json).
- Para ejecutar el backend sin Docker: Python y una instancia accesible de PostgreSQL; el contenedor del backend utiliza Python 3.12.
- Credenciales propias para SMTP y una clave API de Groq cuando se prueben las funciones que las requieren.
4. Variables de entorno y seguridad
Revisar la plantilla backend/.env.example y crear el archivo backend/.env con valores locales, de acuerdo con la configuración efectiva del backend y Docker Compose.
Variable	Uso
DATABASE_URL	Cadena de conexión a PostgreSQL. El host y puerto dependen de si el backend corre dentro o fuera de Docker.
SECRET_KEY	Firma de los tokens JWT; utilizar un secreto largo y aleatorio.
SENDER_EMAIL	Cuenta que envía correos de verificación y recuperación.
SENDER_PASSWORD	Credencial o contraseña de aplicación SMTP.
GROQ_API_KEY	Clave de acceso a Groq para las consultas del asistente.


Verificar también las variables de PostgreSQL utilizadas por docker-compose.yml, si las hubiera; deben permanecer fuera del código fuente y tener valores coherentes con DATABASE_URL. No subir archivos .env, contraseñas, tokens ni claves API a GitHub. La plantilla .env.example debe contener valores ficticios.
5. Ejecución local con Docker Compose
Desde la raíz del repositorio:
docker compose up -d --build api
En el entorno probado, este comando levanta el backend y su dependencia de PostgreSQL. Comprobar el estado con:
docker compose ps
docker compose logs --tail 40 api
A continuación, iniciar el frontend por separado:
npm --prefix ./frontend install
npm --prefix ./frontend run dev
Accesos del entorno local utilizado durante las pruebas:
- Frontend: http://127.0.0.1:5173/app
- Backend: http://127.0.0.1:8000
- Documentación interactiva de FastAPI: http://127.0.0.1:8000/docs
En la configuración local probada, PostgreSQL se publica en 127.0.0.1:5433; dentro de la red de Docker el puerto del servicio es 5432. Comprobar los nombres reales de servicios y los puertos en docker-compose.yml si se modifica el entorno.
6. Ejecución sin Docker
Se requiere PostgreSQL accesible, variables de entorno configuradas y dependencias instaladas.
En una terminal, dentro de backend/:
pip install -r requirements.txt
uvicorn app.main:app --reload
En otra terminal, dentro de frontend/:
npm install
npm run dev
Nota: la configuración de DATABASE_URL cambia según la ubicación de PostgreSQL. Si se utilizan puertos, credenciales o servicios distintos, adaptar las variables de entorno antes de iniciar la API.
7. Uso básico
1. Registrar una cuenta y completar la verificación enviada al correo configurado.
2. Iniciar sesión y abrir Datos (Dashboard).
3. Observar la simulación de métricas y las nuevas alertas; cada evento de WebSocket incorpora su marca de tiempo registrada por el backend.
4. Consultar a J.A.R.V.I.S., por ejemplo: «¿Cuántas anomalías críticas tengo?» o «Analiza mi última alerta crítica y distingue hechos de posibles causas».
5. Abrir Historial y exportar un PDF de los registros cargados.
La conversación mantiene un historial reciente y limitado durante la sesión del frontend; no debe interpretarse como memoria permanente entre sesiones.
Ejemplo de pregunta que requiere consultar la base de datos:
J.A.R.V.I.S., ¿cuántas anomalías críticas tengo registradas? Analiza la última y distingue los datos observados de las posibles causas.

Ejemplo ilustrativo de un mensaje de anomalía (los valores no representan un registro comprobado):
{
  "id": 123,
  "pipeline_name": "Sync PostgreSQL",
  "metric_type": "latencia_ms",
  "value": 725.04,
  "status": "Critico",
  "timestamp": "2026-10-17T09:00:00Z"
}
La opción de vaciar el historial visible puede ocultar registros en la interfaz; esto no equivale necesariamente a eliminarlos de PostgreSQL.
8. Validación y limitaciones
Durante el desarrollo se han realizado pruebas locales de compilación de React, arranque de FastAPI y PostgreSQL con Docker, recepción de telemetría por WebSocket, conversación con Groq y generación de diagnósticos. La auditoría de npm reportó 0 vulnerabilidades después de la actualización aplicada en el entorno de pruebas de octubre de 2026; el resultado puede cambiar conforme se publiquen nuevos avisos.
Limitaciones de esta versión:
- Las métricas y alertas provienen de un simulador, no de AWS, bases productivas u otros servicios reales.
- El diagnóstico de IA es orientativo y puede ser incorrecto; verificar sus hipótesis antes de intervenir sistemas.
- La herramienta actual de J.A.R.V.I.S. consulta estados y registros recientes: no implementa búsqueda general por fechas, métricas, severidades ni análisis histórico arbitrario.
- El asistente depende de la disponibilidad de Groq y está sujeto a límites de uso de su API.
- No hay pruebas documentadas que acrediten preparación para uso productivo, alta disponibilidad o escalabilidad empresarial.
9. Documentación
- [`frontend/README.md`](frontend/README.md): instalación y funcionamiento de la interfaz.
- [`docs/MVP.md`](docs/MVP.md): alcance implementado y criterios de validación del prototipo.
- [`docs/PRD.md`](docs/PRD.md): requisitos, alcance, arquitectura y criterios de aceptación.
10. Lista de comprobación de esta versión
La siguiente lista separa lo implementado de las actividades que siguen pendientes; no equivale a la evaluación final del profesor.
- [x] Ejecutar la simulación automática y registrar anomalías en PostgreSQL.
- [x] Presentar las métricas mediante React y WebSocket autenticado.
- [x] Consultar anomalías por estado a través de J.A.R.V.I.S. 2.0.
- [x] Presentar respuestas Markdown y exportar una bitácora en PDF.
- [x] Documentar las limitaciones de la simulación y la IA.
- [ ] Ejecutar una batería automatizada de pruebas integrales y de seguridad.
- [ ] Integrar fuentes de datos reales (fuera del alcance del MVP actual).
Proyecto académico: PluriOne. Documentación revisada en octubre de 2026.