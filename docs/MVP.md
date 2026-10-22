# Producto Mínimo Viable (MVP) — PluriOne

- **Proyecto:** Plataforma de Observabilidad de Datos con Inteligencia Artificial.
- **Autor señalado en el documento original:** Diego Rivera Aguilar.
- **Periodo:** octubre de 2026.
- **Versión:** prototipo académico con J.A.R.V.I.S. 2.0; consolidación documental del Corte 3 basada en `b5957d4`.

## 1. Alcance del MVP

PluriOne demuestra un ciclo de observabilidad: **simulación o ingesta autenticada de métricas → clasificación → registro de anomalías relevantes → visualización y alertas → consulta orientativa con inteligencia artificial**.

La API recibe métricas con JWT o clave de pipeline; esto es distinto de afirmar que ya existe una conexión automática con AWS o sistemas empresariales de producción. No se ha demostrado tal integración ni una remediación automática sobre infraestructura externa.

### 1.1. Autenticación y seguridad

Registro con contraseñas protegidas mediante hash, verificación de seis dígitos por SMTP, reenvío de códigos, activación de cuentas, inicio de sesión JWT y recuperación de contraseña desde React. Los códigos vencen después de 10 minutos, permiten hasta cinco intentos y se protegen con HMAC. El backend rechaza cuentas inexistentes o inactivas y comprueba el acceso a rutas y eventos WebSocket por usuario.

Las claves de pipeline tienen un mecanismo diferente: se muestran al emitirlas/rotarlas, se almacenan como hash SHA-256 y se verifican usando comparación segura. Su administración en el backend requiere autenticación JWT.

### 1.2. Simulador e ingesta de métricas

El simulador asíncrono de FastAPI genera métricas sintéticas aproximadamente cada 30 segundos para los usuarios activos, sin un botón de inyección manual. Utiliza el mismo servicio de clasificación que la ingesta autenticada. Las anomalías relevantes se guardan en PostgreSQL; las mediciones normales no se persisten como anomalías en el flujo actual.

La API dispone de `POST /metricas/` con JWT y `POST /metricas/externas/` con `X-Pipeline-Key`. La gestión de pipelines ofrece `POST /pipelines/`, `GET /pipelines/`, rotación y revocación de claves. Estas rutas existen en el backend, pero todavía falta una pantalla React para administrarlas.

### 1.3. Dashboard, historial y alertas

React y Recharts presentan latencia, calidad de datos y fallos, con estados Normal, Alerta y Crítico. Los eventos se distribuyen mediante WebSocket autenticado por usuario y el feed muestra la fecha/hora recibida del backend.

El historial puede consultarse, archivarse lógicamente y restaurarse sin eliminación física. Las consultas están protegidas con JWT, filtradas por usuario y paginadas. El PDF exporta los registros cargados en la interfaz; no necesariamente el historial completo de PostgreSQL. También existe una guía de bienvenida.

### 1.4. J.A.R.V.I.S. 2.0

El chat utiliza Groq y el identificador de modelo documentado `openai/gpt-oss-20b`. El backend autoriza una herramienta `consultar_anomalias_usuario`, que devuelve cantidades y hasta diez registros recientes según el estado solicitado (normal, alerta, crítico o todos). El asistente presenta hipótesis de investigación y no certifica causas raíz.

El frontend envía un contexto limitado de mensajes recientes, muestra Markdown con tablas desplazables y ofrece el botón «↓ Último». La conversación no tiene memoria persistente entre sesiones. La IA no analiza automáticamente cada métrica generada: las recomendaciones vinculadas al simulador proceden de reglas/textos locales.

### 1.5. Infraestructura

FastAPI, PostgreSQL, WebSocket y React/Vite funcionan en un entorno local de desarrollo y demostración, con Docker Compose y variables privadas de entorno. Existe un workflow de GitHub Actions con pruebas aisladas y compilación de React. Los Dockerfiles todavía están orientados a desarrollo, no a una instalación empresarial endurecida.

## 2. Estado verificable de las funcionalidades

- **Usuarios, verificación y recuperación:** implementados; se reportaron pruebas manuales del código SMTP, recuperación y nuevo acceso. Códigos con HMAC y separación por propósito.
- **JWT y aislamiento:** implementados; se probaron respuestas HTTP 401 y existen pruebas aisladas para casos de usuarios distintos y WebSocket. No equivale a una auditoría integral.
- **Simulador automático:** implementado con frecuencia aproximada de 30 segundos, no garantizada.
- **Ingesta autenticada:** implementada en la API con JWT o clave de pipeline, validación y clasificación; sin integración continua con sistemas empresariales.
- **Pipelines:** creación, listado, rotación y revocación implementados en el backend; pantalla de React pendiente.
- **Persistencia de anomalías:** implementada en PostgreSQL, con marca de tiempo y estado; las métricas normales no se registran como anomalías en el flujo revisado.
- **WebSocket y dashboard:** implementados, con recepción de eventos y gráficos; falta ampliar pruebas integrales de interfaz.
- **Historial reversible:** archivado lógico, restauración y paginación disponibles. La migración correspondiente aún debe verificarse en una instalación nueva y una existente.
- **J.A.R.V.I.S.:** chat, consultas restringidas y diagnóstico orientativo implementados; sujeto a disponibilidad y límites de Groq.
- **PDF, Markdown y onboarding:** disponibles para los registros y mensajes visibles.
- **Compilación e instalación:** Vite y servicios locales comprobados en revisiones anteriores; hace falta una validación final desde un clon limpio después de integrar todos los cambios.
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

El repositorio revisado contiene **49 funciones de prueba**, pero no todas forman parte de la misma ejecución automática:

- `backend/tests/test_flujos_aislados.py`: **32 pruebas** con `TestClient` y SQLite en memoria. Incluyen expiración, quinto intento, HTTP 429, separación de usuarios, WebSocket y claves de pipelines. **Sí forman parte del workflow actual.**
- `backend/tests/test_integracion_http.py`: **9 pruebas HTTP** de disponibilidad, rutas, autorización, CORS y servicios. **No forman parte del workflow actual; fueron ejecutadas en revisiones anteriores.**
- `backend/tests/test_seguridad_archivado.py`: **8 pruebas** de autorización e historial. **No forman parte del workflow actual; fueron ejecutadas en revisiones anteriores.**

GitHub Actions también instala el frontend con `npm ci` y compila Vite; se confirmó un resultado satisfactorio para el commit `f6a6ab9` de la rama `fix/segunda-auditoria-plurione`. Esto **no demuestra** que las 49 pruebas se hayan ejecutado juntas recientemente ni reemplaza una prueba con PostgreSQL real o una auditoría de producción.

Las comprobaciones manuales descritas en iteraciones anteriores incluyen arranque local de FastAPI/PostgreSQL, compilación de React, recepción de eventos, chat, recuperación SMTP y rechazo de JWT no autorizados. La evidencia debe actualizarse después de las próximas modificaciones del frontend y backend.

## 4. Lista de comprobación del MVP

- [x] Registro, verificación, JWT, recuperación y protección de códigos mediante HMAC.
- [x] Simulador, ingesta de métricas autenticada y clasificación compartida.
- [x] Creación/listado/rotación/revocación de pipelines mediante API.
- [x] PostgreSQL, dashboard y eventos WebSocket segmentados por usuario.
- [x] Archivado y restauración del historial, PDF de los registros visibles y onboarding.
- [x] J.A.R.V.I.S. con Groq, herramientas autorizadas y respuestas Markdown.
- [x] 32 pruebas aisladas en GitHub Actions y compilación de React con CI satisfactorio documentado.
- [ ] Pantalla React de pipelines, configuración `VITE_API_URL` y ejemplo público del entorno frontend.
- [ ] Prueba final del archivado con migraciones en esquemas antiguos y nuevos, con respaldo previo.
- [ ] Integrar las otras 17 pruebas en CI, pruebas con PostgreSQL, lint, carga, navegador y seguridad más amplia.
- [ ] Limitar frecuencia de ingesta y número de pipelines por usuario; continuar modularización.
- [ ] Conectores productivos y remediación automática, fuera del alcance demostrado.

## 5. Exclusiones, riesgos y trabajo posterior

Las métricas del simulador son sintéticas. La ingesta autenticada por API no demuestra la existencia de conectores a AWS o bases empresariales. Las respuestas de IA pueden equivocarse y no sustituyen un diagnóstico técnico. La herramienta de J.A.R.V.I.S. no ofrece filtros históricos arbitrarios ni acceso irrestricto a SQL. El chat no almacena memoria permanente y la exportación PDF solo incluye datos cargados.

Se deben fortalecer la modularización de `main.py` y `App.jsx`, la interfaz de pipelines, los límites de uso y el CI. Los Dockerfiles utilizan configuraciones de desarrollo. Para el archivado, `backend/migrations/001_archivado_logico_anomalias.sql` contiene las columnas `archived` y `archived_at`, pero no se ha confirmado a partir de los documentos que se aplique automáticamente junto con `backend/app/schema_migrations.py` en toda instalación. Antes de manipular un volumen antiguo, respaldarlo y verificar su esquema; nunca usar `docker compose down -v` para conservar datos.

**Uso de IA y tecnología elegida:** el backend implementa Groq; la auditoría menciona Azure como tecnología inicialmente prevista. La aprobación o justificación formal del cambio no está acreditada en la documentación examinada y corresponde confirmarla con el profesor o la empresa. Durante el desarrollo y las auditorías se utilizó asistencia de IA generativa para el análisis y la revisión documental; toda propuesta debe contrastarse con código y pruebas verificables.

## 6. Conclusión y documentos relacionados

El MVP reúne los elementos necesarios para demostrar observabilidad de métricas con entrada autenticada, simulación, seguimiento de anomalías y asistencia conversacional controlada. Su madurez operativa todavía está limitada por la ausencia de conectores productivos, pantalla de pipelines, pruebas integrales y validación de despliegue empresarial.

Documentos relacionados: [`../README.md`](../README.md), [`PRD.md`](PRD.md) y [`../frontend/README.md`](../frontend/README.md).

**Estado documental:** versión consolidada para el tercer corte. Esta actualización reorganiza información del ZIP entregado; no certifica cambios nuevos en el código.
