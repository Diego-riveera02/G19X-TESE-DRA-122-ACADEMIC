# PluriOne — Plataforma de Observabilidad de Datos con Inteligencia Artificial

PluriOne es un prototipo académico funcional de observabilidad de datos. Permite visualizar métricas de pipelines, registrar anomalías, consultar su historial y obtener explicaciones técnicas mediante el asistente conversacional J.A.R.V.I.S., integrado con Groq.

Alcance actual: la telemetría procede de un simulador interno del backend. Las métricas no se capturan de infraestructura empresarial real. Las causas propuestas por la IA son hipótesis para investigar, no incidentes ni causas raíz comprobados.

## 1. Funcionalidades implementadas

Telemetría automática simulada: un proceso asíncrono en FastAPI genera registros de prueba aproximadamente cada 30 segundos, sin depender de botones de inyección manual.

Persistencia: PostgreSQL almacena usuarios y anomalías con identificador, pipeline, métrica, valor, estado, recomendación y fecha de registro.

Monitoreo en tiempo real: React presenta gráficas de latencia, calidad de datos y fallos, junto con un feed de alertas. WebSocket entrega eventos a las sesiones autenticadas del usuario correspondiente.

Acceso a la plataforma: registro y verificación de cuenta por código SMTP, inicio de sesión con JWT, contraseñas almacenadas mediante hash y recuperación de contraseña desde React.

Recuperación de acceso: el usuario solicita un código al correo registrado, lo introduce junto con una contraseña nueva y puede volver a iniciar sesión.

J.A.R.V.I.S. 2.0: chat en español mediante Groq, seguimiento del contexto reciente de la conversación y consultas autorizadas a PostgreSQL mediante function calling.

Consultas de anomalías: la herramienta disponible permite consultar el total y hasta 10 registros recientes del usuario autenticado, filtrados por estado normal, alerta, crítico o todos.

Diagnósticos orientativos: J.A.R.V.I.S. relaciona los datos consultados con posibles causas y acciones de investigación. No confirma causas sin evidencia adicional ni ejecuta cambios en sistemas externos.

Interfaz del asistente: renderizado Markdown con tablas, desplazamiento horizontal dentro de tablas extensas, desplazamiento vertical de la conversación y botón «↓ Último».

Historial y reportes: visualización de anomalías y exportación a PDF de los registros cargados en la interfaz, además de una guía de bienvenida.

Aclaración: la telemetría del simulador utiliza diagnósticos o recomendaciones locales predefinidas. Groq se utiliza para el asistente conversacional; no se realiza una llamada al modelo por cada métrica generada.

## 2. Tecnologías

Backend y API: Python, FastAPI y SQLAlchemy.

Base de datos: PostgreSQL.

Frontend: React, Vite, React Router y Axios.

Gráficas: Recharts.

Actualizaciones en tiempo real: WebSockets autenticados mediante JWT.

Asistente inteligente: Groq API, modelo openai/gpt-oss-20b, con herramientas de consulta controladas por el backend.

Respuestas enriquecidas: react-markdown y remark-gfm.

Reportes: jsPDF y jspdf-autotable.

Contenedores: Docker y Docker Compose.

Imagen del frontend: Node.js 22 Alpine.

## 3. Requisitos previos

Para ejecutar PluriOne se recomienda contar con:

Git, para clonar y actualizar el repositorio.

Docker Desktop y Docker Compose, para ejecutar los servicios contenerizados.

Node.js y npm compatibles con las dependencias declaradas en frontend/package.json.

Python y PostgreSQL para ejecutar el backend sin Docker.

Credenciales SMTP válidas para las funciones de verificación y recuperación.

Una clave API de Groq para utilizar J.A.R.V.I.S.

El contenedor del backend utiliza Python 3.12.

## 4. Variables de entorno y seguridad

PluriOne utiliza dos configuraciones de entorno independientes: una para Docker Compose en la raíz y otra para FastAPI dentro de backend.

### 4.1. Configuración de PostgreSQL en la raíz

El archivo .env.example ubicado en la raíz del repositorio contiene la siguiente variable:

POSTGRES_PASSWORD=

Para preparar una instalación nueva, ejecutar desde la raíz:

Copy-Item .env.example .env

Después, abrir el nuevo archivo .env y asignar una contraseña privada y segura a POSTGRES_PASSWORD.

Docker Compose utiliza esta variable para configurar PostgreSQL y construir la cadena de conexión del backend.

Importante:

No publicar el archivo .env en GitHub.

No introducir contraseñas reales en .env.example.

No sobrescribir un .env existente que ya tenga una configuración funcional.

Si PostgreSQL ya tiene un volumen de datos inicializado, cambiar solamente POSTGRES_PASSWORD en .env no cambia automáticamente la contraseña almacenada en PostgreSQL. Es necesario actualizar ambas configuraciones de manera coordinada.

### 4.2. Configuración del backend

El archivo backend/.env.example sirve como plantilla para las variables utilizadas por FastAPI.

Para preparar una instalación nueva:

Copy-Item backend/.env.example backend/.env

Después, editar backend/.env y configurar los valores privados correspondientes.

Las variables principales son:

DATABASE_URL: cadena de conexión a PostgreSQL. El host y el puerto dependen de si FastAPI se ejecuta dentro o fuera de Docker.

SECRET_KEY: secreto utilizado para firmar los tokens JWT. Debe ser largo, aleatorio y privado.

SENDER_EMAIL: cuenta de correo configurada para enviar códigos de verificación y recuperación.

SENDER_PASSWORD: credencial o contraseña de aplicación del servicio SMTP.

GROQ_API_KEY: clave privada de acceso al servicio Groq.

Cuando FastAPI se ejecuta mediante Docker Compose, DATABASE_URL se establece desde docker-compose.yml utilizando el servicio db y la variable POSTGRES_PASSWORD de la raíz.

Cuando FastAPI se ejecuta directamente en Windows, debe utilizar una dirección de PostgreSQL accesible desde el equipo local.

### 4.3. Protección de credenciales

Los archivos .env son privados y no deben publicarse en GitHub, adjuntarse en entregas ni incluirse en archivos ZIP compartidos.

Los archivos .env.example son plantillas públicas y deben contener únicamente nombres de variables o valores de ejemplo no sensibles.

Si alguna contraseña o clave API se comparte accidentalmente, debe considerarse potencialmente comprometida y renovarse de forma segura.

### 4.4. Autenticación y control de acceso

FastAPI comprueba la firma del JWT, identifica la cuenta correspondiente en PostgreSQL y rechaza el acceso a las rutas protegidas si la cuenta no existe o está inactiva (is_active = False).

Durante las pruebas locales, los endpoints /anomalias/ y /chat/ respondieron HTTP 401 ante solicitudes sin JWT. También se comprobó que una cuenta inactiva recibiera HTTP 401, incluso con un JWT firmado correctamente.

Las operaciones sobre anomalías deben respetar el identificador del usuario autenticado para evitar la exposición de registros de otras cuentas.

## 5. Ejecución local con Docker Compose

### Descargar el código desde GitHub

Para obtener el proyecto en una computadora nueva:

```powershell
git clone https://github.com/Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC.git
cd G19X-TESE-DRA-122-ACADEMIC
```

Después, crear los archivos `.env` a partir de las plantillas
`.env.example` y configurar las credenciales necesarias.
Continuar con las instrucciones de Docker Compose de esta sección.

### Inicialización y migración de PostgreSQL

Al arrancar FastAPI, SQLAlchemy crea las tablas que no existen.

El archivo `backend/app/schema_migrations.py` actualiza las
instalaciones antiguas que todavía no tienen estas columnas:

- `codigo_expira_en`
- `codigo_intentos`
- `codigo_proposito`

La migración se ejecuta al iniciar el backend y conserva los
registros existentes. Puede ejecutarse nuevamente sin duplicar
las columnas.

No ejecutar `docker compose down -v` si se necesitan conservar
los datos de PostgreSQL.


### 5.1. Preparación inicial

Antes de iniciar los servicios, comprobar que existan los archivos privados:

.env en la raíz, con POSTGRES_PASSWORD.

backend/.env, con las variables necesarias para FastAPI, SMTP, JWT y Groq.

Si se trata de un entorno nuevo, generarlos a partir de sus respectivas plantillas .env.example.

No copiar estas plantillas sobre configuraciones existentes sin revisar primero sus valores.

### 5.2. Iniciar PostgreSQL y FastAPI

Desde la raíz del repositorio, ejecutar:

docker compose up -d --build api

Este comando construye o actualiza el backend e inicia su dependencia de PostgreSQL.

El servicio db dispone de una comprobación de salud mediante pg_isready. La API utiliza depends_on con condition: service_healthy para esperar a que PostgreSQL esté disponible antes de comenzar su arranque.

La configuración incluye una política de reinicio unless-stopped para PostgreSQL y FastAPI.

Comprobar el estado de los servicios mediante:

docker compose ps

Revisar los registros del backend mediante:

docker compose logs --tail 40 api

La documentación interactiva de FastAPI se encuentra en:

http://127.0.0.1:8000/docs

Durante las pruebas locales realizadas en octubre de 2026, PostgreSQL alcanzó el estado healthy, FastAPI inició correctamente y /docs respondió HTTP 200.

### 5.3. Ejecutar el frontend

El frontend utiliza React y Vite.

Para ejecutarlo directamente desde Windows:

npm --prefix ./frontend install
npm --prefix ./frontend run dev

El proyecto también incluye un Dockerfile del frontend con Node.js 22 Alpine y un archivo .dockerignore para excluir dependencias locales, archivos temporales y configuraciones privadas del contexto de construcción.

La imagen del frontend se construyó correctamente mediante:

docker compose build frontend

Esta prueba confirma la construcción de la imagen, pero no sustituye una prueba funcional completa del frontend ejecutándose dentro del contenedor.

### 5.4. Direcciones locales

Frontend: http://127.0.0.1:5173/app

Backend: http://127.0.0.1:8000

Documentación FastAPI: http://127.0.0.1:8000/docs

PostgreSQL desde Windows: 127.0.0.1:5433

PostgreSQL dentro de Docker: db:5432

Si se modifican los puertos o los nombres de los servicios, también deben actualizarse las variables de conexión correspondientes.

### 5.5. Conservación de datos

PostgreSQL utiliza un volumen persistente de Docker denominado plurione_postgres_data, asociado al proyecto de Compose.

Para detener los servicios sin eliminar sus datos se puede utilizar:

docker compose stop

No ejecutar docker compose down -v ni eliminar manualmente el volumen cuando se necesite conservar la base de datos.

## 6. Ejecución sin Docker

Se requiere una instancia de PostgreSQL accesible, variables de entorno configuradas y dependencias instaladas.

Desde una terminal ubicada dentro de backend/:

pip install -r requirements.txt
uvicorn app.main:app --reload

En otra terminal, dentro de frontend/:

npm install
npm run dev

La configuración de DATABASE_URL debe corresponder a la ubicación real de PostgreSQL.

Las variables SMTP y Groq deben configurarse antes de utilizar las funciones que dependen de esos servicios.

## 7. Uso básico

Registrar una cuenta y completar la verificación enviada al correo configurado.

Iniciar sesión y abrir la vista Datos (Dashboard).

Si es necesario recuperar el acceso, seleccionar «¿Olvidaste tu contraseña?», escribir el correo registrado y pulsar «Enviar código de recuperación». Después, introducir el código recibido y una nueva contraseña.

Observar las métricas simuladas y las alertas recibidas mediante WebSocket.

Consultar a J.A.R.V.I.S. utilizando preguntas sobre las anomalías registradas.

Abrir el historial y exportar un PDF con los registros cargados.

La conversación con J.A.R.V.I.S. conserva un contexto reciente y limitado durante la sesión del frontend; no debe interpretarse como memoria permanente entre sesiones.

Ejemplo de consulta al asistente

J.A.R.V.I.S., ¿cuántas anomalías críticas tengo registradas? Analiza la última y distingue los datos observados de las posibles causas.

Ejemplo ilustrativo de una anomalía

Los siguientes valores son ilustrativos y no representan un incidente real comprobado.

{
  "id": 123,
  "pipeline_name": "Sync PostgreSQL",
  "metric_type": "latencia_ms",
  "value": 725.04,
  "status": "Critico",
  "timestamp": "2026-10-17T09:00:00Z"
}

El botón Archivar historial archiva las anomalías del usuario en PostgreSQL sin eliminarlas. El botón Restaurar historial permite recuperarlas.

## 8. Validación y limitaciones

### Actualización de la auditoría (octubre de 2026)

- Se comprobó la instalación desde una copia limpia del repositorio, con Docker Compose y un volumen PostgreSQL independiente.
- Se verificó que FastAPI, React y PostgreSQL arrancan correctamente.
- Se incorporaron nueve pruebas automatizadas de integración en `backend/tests/test_integracion_http.py`; las nueve finalizaron satisfactoriamente.
- La verificación y recuperación de cuentas incluyen códigos temporales, un máximo de cinco intentos y propósitos separados.
- El backend incorpora limitación de solicitudes de autenticación respaldada por PostgreSQL y permite reenviar el código de verificación.
- La migración de esquema contempla instalaciones antiguas sin eliminar los registros existentes.
- Estas comprobaciones no equivalen a una auditoría exhaustiva de seguridad ni a una certificación para producción.


### Pruebas automatizadas de integración

Con Docker Compose y los tres servicios iniciados, ejecutar
desde la carpeta raiz del proyecto:

```powershell
python -m unittest discover -s backend/tests -p "test_*.py" -v
```

Las nueve pruebas comprueban disponibilidad de FastAPI y React,
rutas principales, rechazo de tokens JWT ausentes o invalidos,
configuracion CORS y conexion con PostgreSQL.

Estas pruebas necesitan los servicios locales en los puertos
8000 y 5173. No crean usuarios ni modifican registros.
No sustituyen pruebas funcionales completas del navegador,
SMTP, Groq o WebSockets.


### Validaciones realizadas durante el desarrollo

- Compilación del frontend en React.

- Construcción de la imagen Docker del frontend con Node.js 22.

- Arranque de PostgreSQL y comprobación del estado healthy.

- Inicio de FastAPI y respuesta HTTP 200 del endpoint /docs.

- Recepción de telemetría simulada mediante WebSocket.

- Conversación con Groq y generación de diagnósticos orientativos.

- Solicitud del código de recuperación desde React.

- Restablecimiento de contraseña e inicio de sesión con la nueva contraseña.

- Rechazo de peticiones a rutas protegidas sin JWT.

- Rechazo de cuentas inactivas con JWT válido.

- Verificación de cambios mediante Git y sincronización del repositorio.

La auditoría de npm reportó cero vulnerabilidades conocidas durante las comprobaciones realizadas en octubre de 2026. Ese resultado puede cambiar cuando se publiquen nuevos avisos de seguridad.

### Limitaciones conocidas

Las métricas proceden de un simulador interno, no de AWS, bases productivas u otros servicios empresariales reales.

Los diagnósticos de IA son orientativos y pueden ser incorrectos.

La herramienta de J.A.R.V.I.S. consulta estados y registros recientes, pero no implementa búsquedas históricas arbitrarias por fechas, métricas o severidades.

El asistente depende de la disponibilidad de Groq y de los límites de uso de su API.

Los códigos de verificación y recuperación son de seis dígitos, vencen después de 10 minutos y admiten hasta cinco intentos. Se distinguen por propósito, se comparan de forma segura y se invalidan tras su uso.

Todavía no se dispone de una batería completa de pruebas automatizadas que acredite el funcionamiento integral del sistema.

No se ha demostrado preparación para operación empresarial productiva, alta disponibilidad o escalabilidad a gran escala.

## 9. Documentación

- README del frontend: instalación y funcionamiento de la interfaz.

- Producto Mínimo Viable: alcance implementado y criterios de validación.

- Documento de Requisitos del Producto: problemática, objetivos, arquitectura, requisitos y criterios de aceptación.

- docs/Informe Técnico Plataforma de Observabilidad.pdf: informe técnico del desarrollo académico.

- docs/Bitácora de Desarrollo Ágil (Scrum) - Proyecto PluriOne.pdf: registro de actividades y avances del proyecto.

## 10. Lista de comprobación de la versión

Esta lista resume las funcionalidades implementadas y las comprobaciones que todavía están pendientes.

- [x] Ejecutar la simulación automática y registrar anomalías en PostgreSQL.

- [x] Presentar métricas mediante React y WebSocket autenticado.

- [x] Consultar anomalías por estado mediante J.A.R.V.I.S. 2.0.

- [x] Presentar respuestas Markdown y exportar registros en PDF.

- [x] Documentar las limitaciones de la simulación y la inteligencia artificial.

- [x] Solicitar un código SMTP desde React, restablecer la contraseña e iniciar sesión nuevamente.

- [x] Rechazar solicitudes sin JWT y JWT de cuentas inactivas en las rutas protegidas probadas.

- [x] Actualizar la imagen Docker del frontend a Node.js 22.

- [x] Agregar .dockerignore para reducir los archivos enviados a Docker.

- [x] Configurar PostgreSQL con healthcheck y comprobar su estado healthy.

- [x] Comprobar que FastAPI responde HTTP 200 después de iniciar PostgreSQL.

- [x] Crear una plantilla .env.example en la raíz para POSTGRES_PASSWORD.

- [x] Documentar la configuración de variables de entorno para instalaciones nuevas.

- [x] Implementado el vencimiento de códigos y el límite de cinco intentos fallidos.

- [x] Incorporada limitación de solicitudes en endpoints sensibles mediante PostgreSQL.

- [ ] Ejecutar una batería automatizada de pruebas integrales y de seguridad.

- [ ] Comprobar el arranque completo desde un clon limpio del repositorio.

- [ ] Integrar fuentes de datos reales, fuera del alcance del MVP actual.

Proyecto académico: PluriOne — Plataforma de Observabilidad de Datos con Inteligencia Artificial.

Documentación: octubre de 2026.

Estado: prototipo académico funcional en proceso de reforzamiento de seguridad y reproducibilidad.

## Actualizacion de la segunda auditoria - octubre de 2026

### Archivado reversible de anomalias

El sistema permite archivar y restaurar el historial de anomalias sin
eliminar fisicamente los registros de PostgreSQL. El archivado es una
accion solicitada por el usuario; no es una politica de eliminacion
automatica por antiguedad.

Las operaciones del backend son:

- `GET /anomalias/`: consulta las anomalias activas del usuario autenticado.
- `DELETE /anomalias/`: archiva logicamente sus anomalias activas.
- `GET /anomalias/archivadas/`: consulta sus anomalias archivadas.
- `POST /anomalias/restaurar/`: restaura sus anomalias archivadas.

Todas las operaciones anteriores requieren autenticacion JWT y filtran
los registros por usuario. Los listados cuentan con paginacion; de forma
predeterminada, la API devuelve un maximo de 100 registros por consulta.

En React existen controles para archivar y restaurar el historial.
El boton de archivado solicita confirmacion previa. La restauracion
vuelve a mostrar los registros disponibles en la consulta inicial;
no representa necesariamente la totalidad del historial cuando hay
mas de 100 registros.

### Migracion y conservacion de datos

La migracion SQL correspondiente se conserva en
`backend/migrations/001_archivado_logico_anomalias.sql`.
Agrega los campos `archived` y `archived_at` a `anomaly_logs`.

La migracion fue aplicada al entorno local de desarrollo durante la
auditoria. En otra instalacion, comprobar primero si dichas columnas
ya existen y revisar el procedimiento de inicializacion antes de
aplicar la migracion. No ejecutarla nuevamente sobre un esquema
que ya contiene las columnas.

El archivado no sustituye los respaldos de PostgreSQL. No ejecutar
`docker compose down -v` cuando se necesite conservar el volumen.

### Validacion automatizada

En la segunda auditoria se verifico que el frontend compilara con
Vite y que FastAPI respondiera correctamente. El conjunto automatizado
incluye 17 pruebas: nueve pruebas de integracion y ocho pruebas de
seguridad del historial.

Para ejecutar las pruebas con los servicios correspondientes activos:

```bash
python -m unittest discover -s backend/tests -p "test_*.py" -v
```

Las ocho pruebas nuevas verifican el rechazo de solicitudes sin
token y con token invalido, incluidas las operaciones de archivado
y restauracion. No ejecutan archivado autenticado sobre los datos
reales de PostgreSQL.

### Alcance y restricciones

La telemetria procede de un simulador interno, no de infraestructura
productiva. Los resultados de las pruebas no equivalen a una
certificacion de seguridad, pruebas exhaustivas de carga o validacion
integral en un ambiente de produccion. Las operaciones completas
de navegador, correo SMTP y servicios externos requieren verificaciones
adicionales.

### Integración continua con GitHub Actions

El proyecto dispone de integración continua mediante
`.github/workflows/ci.yml`. El workflow se ejecuta al publicar
cambios en `fix/segunda-auditoria-plurione`, al crear una solicitud
de integración hacia `main` y mediante ejecución manual.

- **Backend:** Python 3.12, dependencias de `requirements.txt`
  y pruebas aisladas de `test_flujos_aislados.py` con `unittest`.
  El archivo contiene 32 pruebas y utiliza SQLite aislado.
- **Frontend:** Node.js 24, instalación reproducible mediante
  `npm ci` y compilación de producción con `npm run build`.

La ejecución inicial de GitHub Actions correspondiente al
commit `7de6a10` finalizó correctamente en ambos trabajos.
Esta verificación no representa un despliegue a producción.

El workflow actual no ejecuta `test_integracion_http.py`,
`test_seguridad_archivado.py`, `npm run lint` ni pruebas de carga.
Estas comprobaciones permanecen fuera de su cobertura automática.

## Ingesta de métricas y pipelines

El backend ofrece rutas para registrar métricas mediante JWT y
para recibir datos externos mediante una clave de pipeline.

| Método | Endpoint | Autenticación |
| --- | --- | --- |
| POST | `/metricas/` | JWT del usuario |
| POST | `/metricas/externas/` | Cabecera `X-Pipeline-Key` |
| POST | `/pipelines/` | JWT del usuario |
| GET | `/pipelines/` | JWT del usuario |
| POST | `/pipelines/{pipeline_id}/rotar/` | JWT del usuario |
| POST | `/pipelines/{pipeline_id}/revocar/` | JWT del usuario |

Los endpoints permiten crear y consultar pipelines, rotar o revocar
sus claves y registrar métricas. La existencia de la API no implica
que ya existan conectores completos para sistemas empresariales.

**Límites de uso:** en esta revisión documental aún no se ha
acreditado un límite específico para la ingesta ni un máximo de
pipelines por usuario. Su verificación y fortalecimiento quedan
pendientes de la etapa de seguridad.

Nunca publiques JWT ni claves de pipeline reales en ejemplos,
capturas, documentación o repositorios.
