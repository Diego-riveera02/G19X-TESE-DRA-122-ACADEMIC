# Producto Mínimo Viable (MVP) — PluriOne

- **Proyecto:** Plataforma de Observabilidad de Datos con Inteligencia Artificial.
- **Autor:** Diego Rivera Aguilar.
- **Periodo:** octubre de 2026.
- **Versión:** MVP académico con evidencia integrada en `main` hasta `f95e9e1` (PR #24). Incluye autenticación modularizada y una prueba E2E aislada; la separación posterior de componentes frontend se presenta como cambio adicional.

## 1. Alcance del MVP

PluriOne demuestra un ciclo de observabilidad: **simulación o ingesta autenticada de métricas → clasificación → registro de anomalías relevantes → visualización y alertas → consulta orientativa con inteligencia artificial**.

La API recibe métricas con JWT o clave de pipeline; esto es distinto de afirmar que ya existe una conexión automática con AWS o sistemas empresariales de producción. No se ha demostrado tal integración ni una remediación automática sobre infraestructura externa.

### 1.1. Autenticación y seguridad

Registro con contraseñas protegidas mediante hash, verificación de seis dígitos por SMTP, reenvío de códigos, activación de cuentas, inicio de sesión JWT y recuperación de contraseña desde React. Los códigos vencen después de 10 minutos, permiten hasta cinco intentos y se protegen con HMAC. El backend rechaza cuentas inexistentes o inactivas y comprueba el acceso a rutas y eventos WebSocket por usuario.

Las seis rutas HTTP de identidad están agrupadas en `backend/app/auth_router.py`: registro, verificación, reenvío, solicitud de recuperación, restablecimiento e inicio de sesión. `main.py` conserva la configuración global y el montaje del router. Se mantuvieron las rutas públicas y los controles existentes; no se introdujo un nuevo mecanismo de autenticación.

Las claves de pipeline tienen un mecanismo diferente: se muestran al emitirlas/rotarlas, se almacenan como hash SHA-256 y se verifican usando comparación segura. Su administración en el backend requiere autenticación JWT.

### 1.2. Simulador e ingesta de métricas

El simulador asíncrono de FastAPI genera métricas sintéticas aproximadamente cada 30 segundos para los usuarios activos, sin un botón de inyección manual. Utiliza el mismo servicio de clasificación que la ingesta autenticada. Las anomalías relevantes se guardan en PostgreSQL; las mediciones normales no se persisten como anomalías en el flujo actual.

La API dispone de `POST /metricas/` con JWT y `POST /metricas/externas/` con `X-Pipeline-Key`. La creación, consulta, rotación y revocación de pipelines están implementadas en backend y React. Hay un límite de 20 pipelines activos por usuario y hasta 60 solicitudes por minuto para ingesta. Los endpoints de métricas y pipelines se separaron en `backend/app/metricas_router.py` y `backend/app/pipelines_router.py`.

### 1.3. Dashboard, historial y alertas

React y Recharts presentan latencia, calidad de datos y fallos, con estados Normal, Alerta y Crítico. Los eventos se distribuyen mediante WebSocket autenticado por usuario y el feed muestra la fecha/hora recibida del backend.

El historial puede consultarse, archivarse lógicamente y restaurarse sin eliminación física. Las consultas están protegidas con JWT, filtradas por usuario y paginadas. El PDF exporta los registros cargados en la interfaz; no necesariamente el historial completo de PostgreSQL. También existe una guía de bienvenida.

### 1.4. J.A.R.V.I.S. 2.0

El chat utiliza Groq y el identificador de modelo documentado `openai/gpt-oss-20b`. El backend autoriza una herramienta `consultar_anomalias_usuario`, que devuelve cantidades y hasta diez registros recientes según el estado solicitado (normal, alerta, crítico o todos). El asistente presenta hipótesis de investigación y no certifica causas raíz.

El frontend envía un contexto limitado de mensajes recientes, muestra Markdown con tablas desplazables y ofrece el botón «↓ Último». La conversación no tiene memoria persistente entre sesiones. La IA no analiza automáticamente cada métrica generada: las recomendaciones vinculadas al simulador proceden de reglas/textos locales.

### 1.5. Infraestructura

FastAPI, PostgreSQL, WebSocket y React/Vite componen el entorno local de desarrollo y demostración, con Docker Compose y variables privadas de entorno. GitHub Actions ejecuta 41 pruebas aisladas, ESLint y compilación de React con Node.js 22. Los Dockerfiles todavía están orientados a desarrollo, no a una instalación empresarial endurecida.

## 2. Estado verificable de las funcionalidades

- **Usuarios, verificación y recuperación:** implementados y comprobados manualmente de nuevo después del refactor, incluyendo recepción del código SMTP, cambio de contraseña y acceso posterior. Códigos con HMAC y separación por propósito.
- **JWT y aislamiento:** implementados; se probaron respuestas HTTP 401 y existen pruebas aisladas para casos de usuarios distintos y WebSocket. No equivale a una auditoría integral.
- **Autorización frontend:** `api.js` adjunta JWT a solicitudes Axios privadas y limpia la sesión cuando el token vigente recibe un 401; las rutas públicas de identidad no desencadenan esa redirección. Los flujos habituales se comprobaron manualmente en navegador; siguen pendientes pruebas automatizadas de expiración, concurrencia y escenarios de error.
- **Simulador automático:** implementado con frecuencia aproximada de 30 segundos, no garantizada.
- **Ingesta autenticada:** implementada en la API con JWT o clave de pipeline, validación y clasificación; sin integración continua con sistemas empresariales.
- **Pipelines:** creación, listado, rotación y revocación disponibles en backend y React, comprobadas en escenarios manuales con cuentas distintas. La copia de claves tiene alternativa manual; falta cubrir diferentes permisos y condiciones de navegador.
- **Persistencia de anomalías:** implementada en PostgreSQL, con marca de tiempo y estado; las métricas normales no se registran como anomalías en el flujo revisado.
- **WebSocket y dashboard:** implementados, con recepción de eventos y gráficos; falta ampliar pruebas integrales de interfaz.
- **Historial reversible:** archivado lógico, restauración y paginación disponibles. `schema_migrations.py` no aplica la migración SQL del archivado; su aplicación controlada requiere revisar antes las columnas y respaldar cualquier base existente. El SQL se probó en una tabla antigua mínima simulada; el modelo actual se probó en una base temporal nueva. No se probó una migración integral de todos los esquemas históricos.
- **J.A.R.V.I.S.:** chat, consultas restringidas y diagnóstico orientativo implementados; sujeto a disponibilidad y límites de Groq.
- **PDF, Markdown y onboarding:** disponibles para los registros y mensajes visibles.
- **Compilación e instalación:** frontend y backend verificados localmente. GitHub Actions aprobó pruebas aisladas, ESLint y compilación; la instalación limpia completa aún requiere evidencia independiente.
- **Conectores empresariales, remediación y despliegue de producción:** no demostrados o fuera del MVP.

## 3. Criterios de validación

1. **Acceso controlado:** registro, verificación y recuperación por correo; JWT válido y bloqueo de cuentas inactivas. Códigos temporales con vencimiento, máximo de cinco intentos y propósito específico.
2. **Ingesta reproducible:** envío de una métrica válida mediante `/metricas/` o `/metricas/externas/` y comprobación de su clasificación; los datos normales no tienen por qué aparecer en el historial de anomalías.
3. **Pipelines seguros:** emisión y rotación de claves mostradas una sola vez, revocación y rechazo de claves no válidas, dentro de las pruebas realizadas o por ejecutar.
4. **Simulación automática:** generación periódica sin intervención manual y procesamiento por el mismo servicio que la ingesta.
5. **Aislamiento y tiempo real:** solo el usuario autenticado recibe sus eventos y consulta sus registros.
6. **Historial reversible:** el archivado conserva el registro y la restauración devuelve el estado activo. La paginación no debe confundirse con la totalidad del historial.
7. **Asistente responsable:** J.A.R.V.I.S. recupera datos mediante funciones autorizadas, separa hechos de hipótesis y no opera infraestructura real.
8. **Usabilidad y PDF:** dashboard, chat, tablas y exportación de los registros visibles.
9. **Reproducibilidad:** arranque local siguiendo el README, funcionamiento del esquema nuevo/antiguo y registro de resultados de pruebas sin exponer contraseñas.

### Cobertura de pruebas y evidencia

El repositorio contiene **58 funciones de prueba**, pero no todas forman parte de una misma ejecución automática:

- `backend/tests/test_flujos_aislados.py`: **41 pruebas** con `TestClient` y SQLite en memoria. Incluyen expiración, quinto intento, HTTP 429, separación de usuarios, WebSocket, claves de pipelines y regresiones de routers. **Sí forman parte del workflow actual.**
- `backend/tests/test_integracion_http.py`: **9 pruebas HTTP** de disponibilidad, autorización, rutas, CORS y PostgreSQL. **Aprobadas localmente el 24 de octubre de 2026 con el nuevo router; no se ejecutan en CI.**
- `backend/tests/test_seguridad_archivado.py`: **8 pruebas HTTP** de autorización y archivado. **Aprobadas localmente el 24 de octubre de 2026 con el nuevo router; no se ejecutan en CI.**

GitHub Actions ejecuta 41 pruebas aisladas y comprueba ESLint y compilación de React con Node.js 22. **Los dos trabajos del Pull Request #18 aprobaron el refactor de autenticación.** El 24 de octubre de 2026 aprobaron localmente **41 pruebas aisladas + 9 HTTP + 8 de seguridad = 58 casos**, en tres ejecuciones separadas. No se afirma que las 58 se ejecutaran juntas en CI. El backend reconstruido en Docker expuso las seis rutas y la comprobación HTTP alcanzó PostgreSQL; previamente se creó y verificó un respaldo local, sin realizar una restauración de prueba.

**Pruebas aisladas adicionales de esquema (24 de octubre de 2026):** en un PostgreSQL 16 temporal, el archivo `001_archivado_logico_anomalias.sql` agregó las columnas de archivado a una tabla antigua mínima simulada y conservó su único registro ficticio activo. En otro PostgreSQL 16 temporal se comprobó que SQLAlchemy crea desde cero las tablas `users`, `anomaly_logs`, `auth_rate_limits` y `pipelines` con las columnas de archivado esperadas. Ambos contenedores se eliminaron. En la base principal solo se consultaron las columnas existentes; no se aplicó allí una migración. Faltan pruebas de variantes históricas reales, restauración del respaldo e instalación completa desde un clon limpio.

Se confirmaron manualmente cinco puntos funcionales después del refactor: entrada con cuenta activa, rechazo de contraseña errónea/cierre de sesión, recepción de código SMTP, recuperación y nuevo acceso, y separación de pipelines entre dos usuarios. También se registró una métrica externa autenticada con HTTP 201 en un entorno local. Estas evidencias no son pruebas automáticas de navegador ni certificación de seguridad productiva; deben repetirse cuando cambie el código pertinente.

El cuarto corte cuenta además con una [prueba E2E documentada](PRUEBA_E2E_CORTE4.md) en un clon con Docker Compose aislado: pipeline creado desde React, envío externo con HTTP 201, incremento de anomalías de 27 a 28 en PostgreSQL y alerta visible en el dashboard. Se utilizó una cuenta de prueba activada directamente, sin verificar el circuito SMTP; el entorno requirió preparación adicional a las instrucciones estándar del README.

## 4. Lista de comprobación del MVP

- [x] Registro, verificación, JWT, recuperación y protección de códigos mediante HMAC.
- [x] Simulador, ingesta de métricas autenticada y clasificación compartida.
- [x] Creación/listado/rotación/revocación de pipelines mediante API.
- [x] PostgreSQL, dashboard y eventos WebSocket segmentados por usuario.
- [x] Archivado y restauración del historial, PDF de los registros visibles y onboarding.
- [x] J.A.R.V.I.S. con Groq, herramientas autorizadas y respuestas Markdown.
- [x] 41 pruebas aisladas, 9 HTTP y 8 de seguridad/archivado aprobadas localmente después del refactor; ambos trabajos de CI del PR #18 aprobados.
- [x] Pantalla React de pipelines, configuración `VITE_API_URL` y ejemplo `frontend/.env.example`.
- [x] Flujo E2E de pipeline, ingesta externa, PostgreSQL y dashboard validado en entorno aislado, con evidencia escrita y visual en el PR #24.
- [x] Prueba limitada del SQL de archivado en una tabla antigua mínima simulada y de creación de esquema nuevo mediante SQLAlchemy, usando dos PostgreSQL 16 temporales y aislados.
- [ ] Probar variantes adicionales de esquemas anteriores, restaurar un respaldo de prueba y repetir una instalación completa desde un clon limpio.
- [ ] Incorporar las 17 pruebas HTTP/seguridad al CI con servicios; ESLint ya está integrado. Pendientes pruebas de carga y navegador automatizado.
- [x] Límites de 60 solicitudes por minuto para ingesta y máximo de 20 pipelines activos por usuario.
- [x] Routers de métricas, chat y WebSocket separados de `main.py`, además de anomalías y pipelines.
- [x] Centralizar JWT y HTTP 401 de solicitudes Axios protegidas, manteniendo públicas las rutas de identidad.
- [x] Extraer seis endpoints de autenticación a `backend/app/auth_router.py`, manteniendo la configuración compartida en `main.py` y verificando regresiones.
- [x] Separar `Verificar`, `RecuperarPassword`, el dashboard y el formato de respuestas J.A.R.V.I.S. de `App.jsx`; ESLint y compilación aprobados en la copia revisada.
- [ ] Automatizar la validación del interceptor, expiración de sesión y accesibilidad en navegador; simplificar la lógica interna extensa de `Dashboard.jsx`.
- [ ] Conectores productivos y remediación automática, fuera del alcance demostrado.

## 5. Exclusiones, riesgos y trabajo posterior

Las métricas del simulador son sintéticas. La ingesta autenticada por API no demuestra la existencia de conectores a AWS o bases empresariales. Las respuestas de IA pueden equivocarse y no sustituyen un diagnóstico técnico. La herramienta de J.A.R.V.I.S. no ofrece filtros históricos arbitrarios ni acceso irrestricto a SQL. El chat no almacena memoria permanente y la exportación PDF solo incluye datos cargados.

Se completó la extracción de routers de autenticación, anomalías, pipelines, métricas, chat y WebSocket, la pantalla React de pipelines y la separación de las pantallas principales de `App.jsx`. Persisten tareas de simplificación interna del dashboard, verificación de límites bajo carga y fortalecimiento de CI. Los Dockerfiles siguen orientados a desarrollo. Las columnas de archivado se comprobaron en la base PostgreSQL local. En dos bases temporales aisladas se validaron una migración sobre una tabla antigua mínima simulada y la creación de un esquema nuevo. Sin embargo, `schema_migrations.py` **no ejecuta** `backend/migrations/001_archivado_logico_anomalias.sql`; dicho SQL no es idempotente. Antes de aplicarlo manualmente en otro entorno se debe respaldar la base y comprobar el esquema.

**Uso de IA y tecnología elegida:** el MVP implementa Groq para las respuestas de J.A.R.V.I.S. 2.0 y su llamada controlada a funciones backend. En la propuesta de referencia se plantean servicios Azure, que no se incorporaron al prototipo. Groq permite implementar el flujo conversacional previsto con la integración disponible en FastAPI; la aceptación académica formal de esta sustitución debe confirmarse con el profesor o la empresa. Durante el desarrollo se utilizó IA generativa como apoyo de análisis, programación y documentación; cada resultado requiere revisión y pruebas del equipo.

## 6. Conclusión y documentos relacionados

El MVP demuestra ingesta autenticada, simulación, seguimiento de anomalías, administración de pipelines desde React y asistencia conversacional controlada. Su madurez operativa aún está limitada por la ausencia de conectores productivos, pruebas completas de navegador y validación de despliegue empresarial.

Documentos relacionados: [`../README.md`](../README.md), [`PRD.md`](PRD.md), [`PRUEBA_E2E_CORTE4.md`](PRUEBA_E2E_CORTE4.md) y [`../frontend/README.md`](../frontend/README.md).

**Estado documental:** evidencia integrada hasta `f95e9e1` (PR #24), con autenticación modularizada, dos escenarios limitados de esquema PostgreSQL comprobados en contenedores temporales y una prueba E2E con alerta observada. La separación de componentes frontend es un cambio adicional sujeto a integración. Siguen pendientes una instalación sin preparación adicional siguiendo solamente el README, variantes de migración históricas, restauración del respaldo y pruebas automatizadas de sesión en navegador.
