# Documento de Requisitos del Producto (PRD) — PluriOne

- **Proyecto:** Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne).
- **Empresa vinculada:** PluriOne S.A. de C.V.
- **Autor:** Diego Rivera Aguilar.
- **Periodo:** octubre de 2026.
- **Versión:** código integrado en `main` hasta `657499b` (26 de octubre de 2026), con routers modularizados y validaciones documentadas.

## 1. Propósito, problemática y visión general

En los pipelines de datos, los retrasos, los valores inconsistentes y los fallos pueden pasar inadvertidos si la información está dispersa. PluriOne busca centralizar la recepción y clasificación de métricas, la consulta de anomalías y las alertas para apoyar el seguimiento y la investigación técnica.

El MVP combina **un simulador de demostración** con **endpoints de ingesta autenticada**. Puede aceptar métricas por JWT o clave de pipeline, pero no se ha demostrado que esté conectado de manera permanente con AWS o infraestructura corporativa real. J.A.R.V.I.S. 2.0 ofrece hipótesis orientativas, no confirmaciones autónomas de causas raíz.

## 2. Usuarios y objetivos del producto

**Usuarios previstos:** ingenieros de datos y DataOps que examinan fallos de pipelines, líderes técnicos que consultan indicadores y administradores que supervisan identidades, acceso y pipelines.

**Objetivos específicos:**

1. Registrar y verificar usuarios, autenticar con JWT y permitir la recuperación de contraseña con códigos SMTP protegidos.
2. Recibir métricas desde el simulador y desde clientes autorizados por JWT o clave de pipeline; clasificarlas y almacenar anomalías que requieren seguimiento.
3. Administrar pipelines y sus claves de ingesta mediante alta, consulta, rotación y revocación en FastAPI.
4. Presentar alertas, indicadores y anomalías con segregación por usuario mediante React, PostgreSQL y WebSocket autenticado.
5. Mantener un historial consultable, archivable y restaurable sin eliminación física de registros.
6. Permitir a J.A.R.V.I.S. 2.0 consultar registros autorizados y proporcionar diagnósticos orientativos que diferencien evidencia e hipótesis.
7. Exportar registros visibles a PDF y conservar documentación reproducible de instalación, pruebas y limitaciones.

## 3. Alcance y exclusiones

**Dentro del alcance implementado en el backend y la interfaz actual:**

- Registro, verificación, reenvío de códigos, inicio de sesión JWT, recuperación de acceso y bloqueo de cuentas inactivas.
- Simulador asíncrono de telemetría con un intervalo aproximado de 30 segundos para usuarios activos.
- Ingesta HTTP con JWT (`/metricas/`) o cabecera `X-Pipeline-Key` (`/metricas/externas/`).
- Creación y listado de pipelines, rotación y revocación de sus claves por rutas protegidas con JWT.
- Validación de métricas, clasificación compartida entre simulador e ingesta y persistencia de anomalías relevantes; las mediciones normales no se guardan como anomalías en el flujo revisado.
- Dashboard React/Vite, gráficas, feed con marca temporal de backend y WebSocket autenticado por usuario.
- Consulta, archivado lógico y restauración de historial con filtrado por cuenta y paginación.
- Asistente Groq con function calling limitado a herramientas backend autorizadas, Markdown, onboarding y exportación PDF de registros cargados.
- Docker Compose para demostración y CI con 41 pruebas aisladas, pruebas CORS mediante pytest, ESLint y compilación de React en Node.js 22.

**Fuera del alcance comprobado o pendiente de trabajo:**

- Conectores permanentes a AWS, S3, bases corporativas o sistemas de observabilidad productivos.
- Verificación manual exhaustiva de la interfaz de pipelines, especialmente portapapeles, errores de red y accesibilidad.
- Remediación automática, inspección directa de logs/red/CPU y certificación de causas raíz.
- Consultas conversacionales arbitrarias por fechas, métricas o palabras clave; la herramienta actual filtra por estado.
- Memoria conversacional persistente, alta disponibilidad y garantías operativas empresariales.
- Pruebas exhaustivas de carga, seguridad, navegador y migración de todos los esquemas.
- Garantías de resistencia a abuso bajo carga real y operación productiva de las cuotas actuales.

## 4. Requisitos funcionales e historias de usuario

- **RF-01 — Registro y verificación.** Como usuario nuevo, quiero crear una cuenta y verificarla mediante un código enviado por SMTP. **Estado:** implementado.
- **RF-02 — Acceso y recuperación.** Como usuario, quiero iniciar sesión con JWT y restablecer mi contraseña usando un código recibido por correo desde React. **Estado:** implementado; recuperación SMTP y nuevo acceso comprobados manualmente después de la extracción del router.
- **RF-02A — Revocación de acceso de usuarios inactivos.** Como administrador, quiero que una cuenta inactiva no acceda a rutas protegidas aunque tenga un JWT firmado. **Estado:** implementado y comprobado mediante respuestas HTTP 401 en pruebas locales.
- **RF-03 — Simulación automática.** Como operador, quiero recibir telemetría de prueba sin presionar botones manuales. **Estado:** implementado, aproximadamente cada 30 segundos.
- **RF-04 — Indicadores.** Como operador, quiero visualizar latencia, calidad y fallos. **Estado:** implementado en el dashboard.
- **RF-05 — Eventos por usuario.** Como usuario, quiero recibir solo mis eventos vía WebSocket. **Estado:** implementado y cubierto parcialmente por pruebas aisladas; falta validación exhaustiva de concurrencia.
- **RF-06 — Consulta de anomalías.** Como analista, quiero conocer estado, valor, pipeline y fecha de mis anomalías recientes. **Estado:** implementado.
- **RF-07 — Consulta conversacional.** Como analista, quiero preguntar a J.A.R.V.I.S. por anomalías según su estado. **Estado:** implementado mediante una herramienta backend autorizada que devuelve cantidades y hasta 10 registros recientes.
- **RF-08 — Diagnósticos orientativos.** Como analista, quiero obtener hipótesis y pasos de investigación sin que se presenten como hechos comprobados. **Estado:** implementado con esa limitación.
- **RF-09 — Contexto de chat.** Como usuario, quiero que se conserve el contexto de mis mensajes recientes durante la sesión. **Estado:** implementado de manera temporal, sin persistencia permanente.
- **RF-10 — Lectura accesible del contenido.** Como usuario, quiero ver mensajes Markdown, tablas desplazables y un control para llegar al último mensaje. **Estado:** implementado; pruebas completas de accesibilidad pendientes.
- **RF-11 — Exportación y seguimiento.** Como usuario, quiero revisar mi historial y exportar lo visible a PDF. **Estado:** implementado; no exporta necesariamente el historial completo si está paginado.
- **RF-12 — Bienvenida.** Como usuario nuevo, quiero una guía de incorporación. **Estado:** implementado.
- **RF-13 — Archivado reversible.** Como usuario autenticado, quiero archivar mis anomalías sin borrarlas y restaurarlas posteriormente. **Estado:** implementado con JWT, filtrado por usuario, paginación y controles en React; la migración debe comprobarse en cada instalación.
- **RF-14 — Ingesta de métricas.** Como operador, quiero registrar métricas mediante mi JWT o una clave de pipeline emitida para un cliente externo. **Estado:** implementado en la API; sin conectores corporativos ni validación de carga productiva.
- **RF-15 — Gestión de pipelines.** Como propietario, quiero crear, listar, rotar y revocar claves. **Estado:** implementado en FastAPI y React; faltan pruebas exhaustivas de navegador y escenarios de error.

### Requisitos no funcionales

- **RNF-01 — Seguridad:** contraseñas con hash, JWT, identidad activa, secretos fuera de Git y validación de entradas.
- **RNF-02 — Aislamiento:** anomalías, pipelines y WebSocket asociados al usuario autenticado; nunca utilizar un identificador de usuario generado libremente por el modelo.
- **RNF-03 — Tiempo real:** entrega por WebSocket sin necesidad de recarga, sin promesa de latencia máxima.
- **RNF-04 — Persistencia y trazabilidad:** guardar anomalías y su fecha, conservar el archivado reversible y proteger los datos existentes al migrar.
- **RNF-05 — Usabilidad:** gráficas, feed, chat y tablas legibles, con desplazamiento dentro de su área.
- **RNF-06 — IA responsable:** diferenciar telemetría sintética, registros observados e hipótesis; no atribuir inspecciones externas inexistentes.
- **RNF-07 — Protección de credenciales:** códigos de un solo uso con HMAC; claves de pipelines almacenadas mediante hash SHA-256 y comparación segura; evitar exposición de secretos.
- **RNF-08 — Control de abuso:** límites de intentos y solicitudes sensibles, máximo de 20 pipelines activos por usuario y límite de 60 solicitudes por minuto para ingesta; falta validar su eficacia bajo carga y concurrencia reales.
- **RNF-09 — Reproducibilidad:** variables de entorno documentadas, dependencias fijadas y ejecución verificable con Docker y CI.
- **RNF-10 — Mantenibilidad:** URL HTTP/WebSocket, JWT y respuesta HTTP 401 de Axios centralizados; routers independientes para autenticación, anomalías, pipelines, chat, métricas y WebSocket. `main.py` conserva la configuración compartida y registra los routers. `App.jsx` ya está modularizado; sigue pendiente dividir `Dashboard.jsx` y ampliar las pruebas automatizadas de interfaz.

## 5. Arquitectura y flujo de datos

- **Adquisición:** simulador FastAPI o `POST /metricas/`/`POST /metricas/externas/`, con validaciones y autenticación distintas.
- **Procesamiento:** función `registrar_metrica` compartida para clasificar eventos; las mediciones normales no se persisten como anomalías en el flujo implementado.
- **Persistencia:** PostgreSQL y SQLAlchemy para usuarios, anomalías y gestión de pipelines.
- **Distribución:** WebSocket autorizado por usuario y consultas HTTP paginadas.
- **Presentación:** React, Vite, Axios, React Router, Recharts, Markdown y PDF.
- **IA:** Groq y el identificador `openai/gpt-oss-20b`, mediante herramientas de consulta controladas por el backend. El simulador no realiza una llamada de IA por cada registro.
- **Identidad:** SMTP para códigos temporales, JWT y controles sobre cuentas inactivas.
- **Organización del backend:** `backend/app/auth_router.py` define las seis rutas de identidad (registro, verificación, reenvío, solicitud de recuperación, cambio de contraseña y login); `backend/app/main.py` registra el router e inyecta sus dependencias compartidas. La reorganización mantiene los contratos HTTP y las reglas de seguridad del MVP.

**Flujo de observabilidad:** cliente o simulador → autenticación y validación → clasificación → persistencia de anomalías relevantes → WebSocket/HTTP → React. **Flujo de chat:** usuario con JWT → `/chat/` → Groq → herramienta permitida ejecutada por FastAPI → resultado autorizado → respuesta en React.

**Endpoints relevantes:**

- `POST /metricas/` — ingesta con JWT.
- `POST /metricas/externas/` — ingesta con `X-Pipeline-Key`.
- `POST /pipelines/`, `GET /pipelines/` — crear y consultar pipelines con JWT.
- `POST /pipelines/{pipeline_id}/rotar/` y `POST /pipelines/{pipeline_id}/revocar/` — rotar o revocar con JWT.
- `GET /anomalias/`, `DELETE /anomalias/`, `GET /anomalias/archivadas/`, `POST /anomalias/restaurar/` — historial protegido y reversible.

Estas rutas forman parte del código del MVP. La ingesta y las alertas ya tienen una prueba E2E documentada en [`PRUEBA_E2E_CORTE4.md`](PRUEBA_E2E_CORTE4.md). Continúa pendiente una instalación desde cero siguiendo literalmente el README, sin activar cuentas directamente en PostgreSQL.

## 6. Seguridad y uso responsable de inteligencia artificial

Los códigos SMTP de verificación y recuperación expiran después de 10 minutos, se limitan a cinco intentos y se separan por propósito. Su protección usa HMAC y `hmac.compare_digest` en `backend/app/verification_codes.py`. Las claves emitidas para pipelines son diferentes: `backend/app/pipeline_keys.py` utiliza SHA-256 y `hmac.compare_digest`. La clave debe copiarse al emitirla o rotarla, sin registrar su texto completo en la base de datos ni en documentos.

El backend también incorpora autenticación JWT, rechazo de usuarios inactivos, limitación de solicitudes de autenticación, ingesta limitada a 60 solicitudes por minuto y un máximo de 20 pipelines activos por cuenta. La recuperación no revela públicamente si existe una cuenta. **Pendientes:** pruebas de carga, revisión de posibles carreras de concurrencia y auditoría integral de seguridad.

**Elección tecnológica:** el prototipo utiliza Groq para generar respuestas y realizar llamadas controladas a funciones backend en J.A.R.V.I.S. 2.0. La propuesta empresarial de referencia menciona Azure OpenAI Service y otras herramientas Azure; esas integraciones no forman parte del MVP implementado. Esta sustitución permite demostrar el flujo conversacional y su autorización desde FastAPI sin depender de servicios empresariales Azure. Se debe conservar la justificación académica y confirmar su aceptación formal con el profesor o la empresa; no se afirman ventajas de costo o rendimiento no medidas.

**Declaración de asistencia:** durante el desarrollo y la revisión se utilizó IA generativa como apoyo para el análisis, propuestas de código y documentación. Las modificaciones deben contrastarse con el repositorio y las pruebas; el equipo conserva la responsabilidad técnica y académica.

## 7. Plan de trabajo y evolución

- **Datos y persistencia:** modelos PostgreSQL y registro de anomalías implementados; `schema_migrations.py` actualiza columnas de autenticación, pero **no** ejecuta el SQL de archivado. El SQL se comprobó sobre una tabla antigua mínima con un registro ficticio; el modelo SQLAlchemy creó un esquema nuevo en otro PostgreSQL 16 aislado. Comprobar el esquema en cada instalación y aplicar la migración manual controlada cuando corresponda; faltan otras variantes históricas y una restauración de respaldo de prueba.
- **Backend y seguridad:** autenticación, ingesta, pipelines, HMAC, aislamiento, límites de ingesta y de pipelines y routers de autenticación, anomalías, pipelines, métricas, chat y WebSocket implementados. La extracción de autenticación aprobó pruebas de regresión locales. Pendiente una auditoría integral de seguridad.
- **Interfaz y observabilidad:** dashboard, WebSocket, chat, historial, PDF y gestión React de pipelines implementados. URL del backend y token/401 HTTP centralizados en `api.js`. Los flujos habituales de autenticación se comprobaron manualmente; pendientes accesibilidad y pruebas automatizadas de navegador, incluida la expiración de sesión.
- **Empaquetamiento y reproducibilidad:** Docker Compose, ejemplos de entorno y CI disponibles en `main`; 41 pruebas aisladas, ESLint y compilación de React aprobados en los dos trabajos del Pull Request #18, ya integrado. Con el refactor aprobaron localmente 41 pruebas aisladas y 17 pruebas HTTP/seguridad. Dos escenarios de esquema aprobaron en contenedores PostgreSQL 16 temporales independientes, sin modificar la base principal. Pendientes CI con PostgreSQL real, instalación desde clon limpio, restauración de respaldo y revisión de contenedores productivos.
- **Evolución posterior:** conectores productivos, búsqueda histórica avanzada, alta disponibilidad, pruebas de carga y remediación, fuera del alcance comprobado.

## 8. Criterios de aceptación y evidencia

- **CA-01:** la API inicia y el simulador genera métricas sin intervención manual.
- **CA-02:** ingesta por JWT o clave válida de pipeline, con validación de entradas y clasificación compartida.
- **CA-03:** solo el usuario autorizado consulta y recibe sus anomalías vía HTTP/WebSocket.
- **CA-04:** el feed utiliza la fecha del registro, no una fecha inventada por el navegador.
- **CA-05:** el asistente consulta únicamente mediante herramientas autorizadas y distingue hipótesis de observaciones.
- **CA-06:** el chat presenta Markdown y tablas desplazables; el historial visible se puede exportar a PDF.
- **CA-07:** los códigos, las rutas privadas y las cuentas inactivas cumplen sus reglas de acceso.
- **CA-08:** las operaciones de archivado y restauración conservan los registros y su pertenencia al usuario; las rutas admiten paginación.
- **CA-09:** las claves de pipelines se emiten, rotan y revocan sin almacenarse en claro.
- **CA-10:** Docker/README permiten repetir el arranque, los cambios de esquema se verifican sin destruir datos y las pruebas automatizadas son trazables.
- **CA-11:** las decisiones y limitaciones de IA están documentadas sin atribuir monitoreo empresarial no demostrado.

**Evidencia disponible y límites:** la validación histórica reunió 58 casos en tres suites: 41 aisladas, 9 de integración HTTP y 8 de seguridad/archivado. El repositorio de referencia contiene seis archivos de pruebas, incluyendo los de CORS, SMTP y plantillas de correo. Las 41 aisladas, ESLint y compilación del frontend aprobaron en GitHub Actions para el Pull Request #18, que incorporó la extracción de autenticación. Después del refactor, las tres suites aprobaron localmente el 24 de octubre de 2026: **58 de 58 casos en ejecuciones separadas**. Las 17 pruebas HTTP/seguridad no se ejecutan en el workflow actual y la evidencia local no sustituye pruebas de carga, navegador automatizado o producción.

Las pruebas aisladas incluyen casos de vencimiento de códigos, quinto intento, respuesta 429, aislamiento entre usuarios, WebSocket y rotación/revocación de pipelines. Además, con la API reconstruida en Docker se validaron sus rutas y la conexión con PostgreSQL. Se confirmaron manualmente cinco flujos: login, rechazo de credenciales erróneas, recuperación por correo, inicio de sesión con contraseña nueva y separación de pipelines entre cuentas. Esto no acredita pruebas exhaustivas de PostgreSQL, carga, navegador automatizado, SMTP a gran escala y servicios externos; tampoco constituye certificación empresarial.

**Evidencia de migración aislada:** el 24 de octubre de 2026, un PostgreSQL 16 temporal sin acceso a la red ni a los volúmenes de PluriOne permitió ejecutar `001_archivado_logico_anomalias.sql` sobre una tabla antigua mínima simulada. Se mantuvo su único registro ficticio y quedó activo (`archived = FALSE`, `archived_at = NULL`). En otro PostgreSQL 16 temporal y separado, SQLAlchemy creó las tablas `users`, `anomaly_logs`, `auth_rate_limits` y `pipelines` con las columnas de archivado. Ambos entornos se eliminaron; la base principal solo se inspeccionó en modo lectura y ya contenía las columnas. Estas pruebas no acreditan la migración de todas las variantes históricas, una restauración del respaldo ni la instalación completa desde un clon limpio.

## 9. Riesgos y restricciones

- Diagnósticos sujetos a errores del modelo y a la calidad de las métricas disponibles.
- Simulación sintética y ausencia de conectores empresariales permanentes.
- Dependencia de proveedores Groq/SMTP y cuotas de servicio.
- Paginación: la primera consulta o el PDF puede no incluir todos los registros de la base de datos.
- Migración de archivado SQL separada (`backend/migrations/001_archivado_logico_anomalias.sql`): **no se ejecuta desde `schema_migrations.py`**. Su SQL incorpora columnas sin `IF NOT EXISTS`, por lo que no debe repetirse a ciegas. Aprobó una simulación limitada con una tabla antigua mínima, pero faltan verificaciones de otras versiones históricas y restauración de respaldo. En una base de datos existente se debe verificar el esquema y hacer respaldo antes de aplicarlo manualmente si falta.
- Pendientes pruebas manuales de portapapeles, concurrencia y resistencia bajo carga de los límites de ingesta y cantidad de pipelines.
- CI con SQLite en memoria para las 41 pruebas aisladas y ejecución adicional de pruebas CORS mediante pytest; ESLint y build activos. Pendiente incorporar pruebas SMTP, plantillas de correo y pruebas HTTP/archivado con los servicios correspondientes.
- Dockerfiles todavía orientados a desarrollo; la preparación para producción no está demostrada.

## 10. Lista de verificación del producto

- [x] Registro, verificación, JWT, recuperación y rechazo de usuarios inactivos.
- [x] Simulador, endpoints de ingesta y administración de pipelines en el backend.
- [x] WebSocket por usuario, dashboard, archivado lógico, restauración, chat y PDF.
- [x] Códigos con HMAC y claves de pipeline con SHA-256.
- [x] CI con 41 pruebas aisladas, pruebas CORS, ESLint y compilación de frontend. Los dos trabajos del Pull Request #18 aprobaron el refactor de autenticación; las pruebas CORS se incorporaron posteriormente.
- [x] Interfaz React de pipelines y configuración centralizada de API/WebSocket.
- [x] Cuota de hasta 20 pipelines activos por usuario y límites de 60 solicitudes de ingesta por minuto implementados.
- [x] Routers de autenticación, pipelines, métricas, chat, anomalías y WebSocket extraídos de `main.py`, con configuración compartida preservada.
- [x] Centralizar la autorización JWT y el cierre por HTTP 401 de solicitudes Axios protegidas, sin redirigir ante un 401 de login público.
- [x] Extraer las seis rutas de identidad a `auth_router.py` y repetir las 58 pruebas locales y los flujos esenciales de autenticación.
- [x] Modularizar `App.jsx` en componentes independientes.
- [ ] Automatizar pruebas del interceptor, sesión y accesibilidad en navegador.
- [x] Verificar el SQL de archivado en una tabla antigua mínima simulada y el esquema nuevo generado por SQLAlchemy, con PostgreSQL 16 temporal aislado en ambos casos.
- [ ] Verificar variantes históricas adicionales, restaurar un respaldo en un entorno de prueba e instalar todo el sistema desde un clon limpio.
- [ ] Ampliar CI con PostgreSQL y pruebas HTTP/seguridad; la ejecución en `main` y ESLint ya están configurados.
- [ ] Conectores productivos, pruebas de carga, seguridad integral y eventual despliegue empresarial.

## 11. Documentos relacionados

- [`../README.md`](../README.md) — instalación, configuración, ingesta, seguridad y pruebas.
- [`MVP.md`](MVP.md) — alcance actual y criterios de validación del producto mínimo viable.
- [`../frontend/README.md`](../frontend/README.md) — instalación y capacidades de la interfaz.

**Estado:** código integrado en `main` hasta `657499b`, con autenticación modularizada, evidencia E2E documentada y dos escenarios limitados de migración/creación de esquema comprobados sobre PostgreSQL 16 temporal. Continúan pendientes la instalación completa desde un clon limpio, pruebas automatizadas de sesión en navegador, variantes históricas de migración, restauración de respaldo y confirmación formal de las sustituciones tecnológicas.
