# Frontend de PluriOne

**Frontend del MVP académico · Octubre de 2026.** Referencia actual: `main` hasta `3cbc283` (Corte 6). La interfaz React permite registrar y autenticar usuarios, administrar pipelines, consultar métricas y anomalías, utilizar J.A.R.V.I.S. 2.0, revisar el historial y exportar información a PDF. `Dashboard.jsx` fue modularizado y quedó en 391 líneas.

El backend dispone de ingesta autenticada y gestión de pipelines. React incorpora una pantalla para crear, listar, rotar y revocar pipelines. El frontend no se conecta directamente a PostgreSQL ni a infraestructuras empresariales.

## 1. Tecnologías y componentes

- **React y Vite:** interfaz y entorno de desarrollo.
- **React Router:** navegación entre inicio de sesión, registro, verificación, recuperación y dashboard.
- **Axios:** comunicación con FastAPI.
- **Recharts:** indicadores y gráficas de telemetría.
- **WebSocket:** notificaciones de anomalías después de autenticar la sesión.
- **react-markdown y remark-gfm:** respuestas del asistente con títulos, listas y tablas.
- **jsPDF y jspdf-autotable:** exportación de la bitácora cargada.

## 2. Funcionalidades implementadas

- **Identidad:** registro, verificación con código SMTP, reenvío mediante `POST /reenviar-verificacion/`, inicio de sesión y recuperación de acceso.
- **Dashboard:** indicadores de latencia, calidad de datos y fallos con estados Normal, Alerta y Crítico.
- **Alertas:** feed con hora del registro enviada por FastAPI y recepción WebSocket autenticada y segmentada por usuario. La autorización real depende del backend, no solo de filtros React.
- **Historial:** consulta de anomalías activas, archivado lógico con confirmación y restauración; las listas son paginadas y el PDF representa los registros cargados en la interfaz.
- **J.A.R.V.I.S. 2.0:** preguntas a `/chat/` con JWT, hasta 10 mensajes anteriores enviados como contexto durante la sesión, visualización Markdown y tablas desplazables.
- **Navegación del chat:** desplazamiento de la conversación, desplazamiento horizontal dentro de tablas y botón «↓ Último».
- **Onboarding:** guía de bienvenida para nuevos usuarios.

El simulador de FastAPI genera métricas sintéticas aproximadamente cada 30 segundos; el backend puede recibir además métricas por JWT o por clave de pipeline. Una medición clasificada como normal no necesariamente se almacena como anomalía. La interfaz muestra los datos disponibles desde las consultas y eventos que el servidor entrega.

## 3. Requisitos e instalación

Se necesitan Node.js y npm compatibles con las dependencias declaradas, un backend FastAPI configurado y PostgreSQL disponible para ese backend. El navegador **no** debe conectarse directamente a la base de datos.

Desde la carpeta `frontend/`:

```powershell
npm install
npm run dev
```

O desde la raíz del repositorio:

```powershell
npm --prefix ./frontend install
npm --prefix ./frontend run dev
```

En el entorno local descrito se utilizó `http://127.0.0.1:5173/app`. Para compilar:

```powershell
npm --prefix ./frontend run build
```

Docker Compose también permite construir/ejecutar los servicios configurados desde la raíz:

```powershell
docker compose up -d --build
```

Esta configuración utiliza contenedores de **desarrollo/demostración**. La imagen frontend se describe con Node.js 22 Alpine y arranque de desarrollo; su construcción no demuestra una implementación productiva. No ejecutar `docker compose down -v` si se necesita conservar el volumen de PostgreSQL.

Si Vite muestra una advertencia de chunks grandes, eso no significa automáticamente que la compilación haya fallado, aunque puede señalar oportunidades de optimización.

## 4. Comunicación con el backend

En la configuración local utilizada:

- HTTP: `http://127.0.0.1:8000`
- WebSocket: `ws://127.0.0.1:8000/ws/anomalias`
- Frontend: `http://127.0.0.1:5173`

La conexión HTTP y WebSocket está centralizada en `frontend/src/api.js` mediante `import.meta.env.VITE_API_URL`, con valor de ejemplo en `frontend/.env.example`. Para desarrollo local, copiar el ejemplo a `frontend/.env` y ajustar `VITE_API_URL` cuando sea necesario; reiniciar Vite después de cambiarla. Un interceptor Axios añade `Authorization: Bearer` a las solicitudes privadas cuando existe un token y otro limpia la sesión y redirige a `/login` si ese token recibe HTTP 401. Se excluyen las rutas públicas de registro, verificación, login y recuperación; también se evita enviar el token a otro origen o cerrar una sesión nueva por la respuesta tardía de un token anterior. Se comprobaron manualmente login y recuperación en navegador después del refactor del backend; siguen pendientes pruebas automatizadas de tokens expirados, respuestas tardías y errores de red.

### Rutas relevantes para la interfaz

- `GET /anomalias/`, `GET /anomalias/archivadas/`: consultas de historial protegidas con JWT.
- `DELETE /anomalias/`, `POST /anomalias/restaurar/`: archivado y restauración.
- `POST /chat/`: conversación autenticada con herramientas restringidas por FastAPI.
- `POST /solicitar-recuperacion/`: solicitud pública de código para recuperar acceso; la respuesta del backend no debe revelar si el correo existe.
- `POST /recuperar-password/`: comprobación del código y actualización de contraseña.
- `POST /reenviar-verificacion/`: reenvío del código de activación.
- `ws://127.0.0.1:8000/ws/anomalias`: eventos tras autenticación por mensaje JWT.

Ejemplo **estructural** del primer mensaje WebSocket (token deliberadamente ficticio):

```json
{"type":"auth","token":"TOKEN_JWT_DE_EJEMPLO"}
```

El backend valida el JWT antes de distribuir anomalías asociadas al usuario. El feed muestra el campo `timestamp` de cada registro en hora local del navegador cuando corresponde.

### Recuperación de acceso

1. Desde Login, abrir «¿Olvidaste tu contraseña?».
2. Introducir el correo y solicitar un código; evitar solicitudes duplicadas mientras la operación está en curso.
3. Consultar el mensaje SMTP más reciente y enviar el código de seis dígitos con la nueva contraseña.
4. Volver a iniciar sesión con la contraseña actualizada.

El flujo se comprobó nuevamente de forma manual en el entorno local el 24 de octubre de 2026: recepción del código SMTP, establecimiento de contraseña nueva e inicio de sesión posterior. Los códigos tienen vencimiento, máximo de cinco intentos y separación por propósito, implementados en FastAPI. Las seis rutas de identidad ahora se encuentran en `backend/app/auth_router.py`, montado desde `backend/app/main.py`; el frontend conserva las mismas URLs públicas.

## 5. Dashboard, IA y alcance de pipelines

J.A.R.V.I.S. 2.0 permite preguntas generales sobre observabilidad y consultas autorizadas de anomalías del usuario. Su herramienta devuelve totales y hasta 10 registros recientes, filtrados por estado. No dispone de consultas arbitrarias por fecha o métrica ni de memoria permanente entre sesiones. Las explicaciones sobre posibles causas son orientativas.

La administración de pipelines existe en FastAPI y en `frontend/src/Pipelines.jsx`. La interfaz permite crear, listar, rotar y revocar claves. Las claves se muestran al emitirlas o rotarlas; el botón de copia ofrece una alternativa de selección manual cuando el navegador bloquea la copia automática. Su funcionamiento debe comprobarse manualmente en el navegador.

Los códigos de verificación usan HMAC en el backend; las claves de pipeline usan SHA-256 y comparación segura. **Estas funciones de seguridad pertenecen al servidor** y no autorizan almacenar secretos en el código o en el repositorio del frontend.

## 6. Comprobaciones y cobertura de pruebas

El repositorio contiene 58 funciones de prueba en backend:

- **41 aisladas** en `test_flujos_aislados.py`, con SQLite en memoria: se ejecutan en el CI actual.
- **9 HTTP** en `test_integracion_http.py`: necesitan los servicios correspondientes y no se ejecutan en el workflow actual.
- **8 de seguridad/archivado** en `test_seguridad_archivado.py`: fuera del workflow actual.

GitHub Actions aprobó las 41 pruebas aisladas del backend y las comprobaciones de ESLint y compilación React para el Pull Request #18, que incorporó el refactor de autenticación. Con ese refactor, el 24 de octubre de 2026 aprobaron localmente y por separado las 41 pruebas aisladas, 9 de integración HTTP y 8 de seguridad/archivado: **58 casos satisfactorios**. También se verificaron manualmente cinco flujos principales de identidad y separación de cuentas. Las 17 pruebas HTTP/seguridad no forman parte del workflow actual; estos resultados no equivalen a pruebas exhaustivas de navegador, SMTP, carga o accesibilidad.

Comandos útiles desde la raíz:

```powershell
npm --prefix ./frontend run build
npm --prefix ./frontend run lint
npm --prefix ./frontend audit
```

ESLint se ejecuta localmente y forma parte del workflow actual de GitHub Actions. Continúan pendientes pruebas automatizadas de navegador y accesibilidad. Una auditoría npm anterior reportó cero vulnerabilidades conocidas, resultado que puede cambiar con nuevos avisos.

La suite HTTP requiere API, frontend y PostgreSQL iniciados; ejecutar todas las pruebas mediante descubrimiento global puede requerir preparar previamente entornos diferentes. Para pasos reproducibles de instalación y detalles de CI, consultar el README raíz.

## 7. Seguridad, limitaciones y trabajo pendiente

- La URL de API y WebSocket está centralizada; es necesario configurar `VITE_API_URL` correctamente en cada entorno.
- El token JWT y las respuestas HTTP 401 de solicitudes Axios están centralizados en `api.js`; el WebSocket mantiene su autenticación inicial por mensaje JWT. El inicio de sesión y la recuperación funcionaron manualmente después de la extracción del router; faltan pruebas automatizadas de expiración, recuperación de sesión y respuestas concurrentes.
- La pantalla de pipelines existe; falta ampliar las pruebas manuales de copia, errores y accesibilidad.
- `App.jsx` contiene solamente las rutas. Las pantallas `Verificar.jsx`, `RecuperarPassword.jsx`, `Dashboard.jsx` y `RespuestaJarvis.jsx` se separaron manteniendo sus llamadas API y comportamiento. La lógica interna del dashboard todavía es extensa y puede simplificarse en futuros cambios.
- Faltan pruebas automatizadas completas de navegador, accesibilidad y estados de error; ESLint ya se ejecuta en CI.
- El historial PDF puede reflejar solo una página de registros.
- La interfaz no confirma incidentes productivos ni ejecuta acciones correctivas en sistemas externos.
- La seguridad real de JWT, WebSocket, claves y aislamiento se valida en FastAPI y no debe depender de controles visuales.

El MVP utiliza **Groq** en el backend para generar respuestas de J.A.R.V.I.S. y permitir consultas de anomalías mediante una herramienta autorizada. La propuesta empresarial de referencia contempla servicios Azure, que no se integraron al prototipo; esta sustitución técnica debe justificarse y confirmarse académicamente con el profesor o la empresa. Durante el desarrollo se utilizó IA generativa como apoyo documental y técnico; los resultados se contrastan con el código y las pruebas.

## 8. Referencias y lista de verificación

- [`../README.md`](../README.md): descripción general, variables, instalación y API.
- [`../docs/PRD.md`](../docs/PRD.md): requisitos y criterios de aceptación.
- [`../docs/MVP.md`](../docs/MVP.md): alcance y evidencia del prototipo.
- [`../docs/PRUEBA_E2E_CORTE4.md`](../docs/PRUEBA_E2E_CORTE4.md): ingesta E2E con pipeline, PostgreSQL y alerta en React, más captura.
- [`../docs/VALIDACION_CLON_LIMPIO_CORTE4.md`](../docs/VALIDACION_CLON_LIMPIO_CORTE4.md): arranque del frontend desde clon nuevo y limitación CORS del puerto alternativo.

- [x] Registro, verificación, recuperación y acceso JWT.
- [x] Dashboard, alertas, WebSocket por usuario y chat Markdown.
- [x] Historial reversible, exportación PDF y onboarding.
- [x] Compilación de producción del frontend confirmada en GitHub Actions.
- [x] Pantalla de administración de pipelines.
- [x] Centralización de API/WebSocket y creación de `frontend/.env.example`.
- [x] ESLint y compilación de React aprobados en el CI del Pull Request #18, que incorporó el refactor de autenticación.
- [x] Centralizar el token y la respuesta HTTP 401 mediante interceptores Axios.
- [x] Extraer verificación, recuperación, dashboard y formato de respuestas de J.A.R.V.I.S. de `App.jsx`; ESLint y compilación aprobados en la copia revisada.
- [x] Verificar manualmente en navegador login, rechazo de contraseña incorrecta, recuperación SMTP y acceso con contraseña nueva tras el refactor de autenticación.
- [ ] Automatizar las pruebas de navegador del interceptor, expiración de JWT y recuperación de sesión.
- [x] Modularizar `Dashboard.jsx` hasta 391 líneas y separar componentes. Permanecen pendientes ampliar las pruebas de interfaz y accesibilidad.

**Estado:** frontend modularizado y backend actualizado hasta `3cbc283`; 43 pruebas aisladas, 18 pruebas CORS y 7 pruebas de correo aprobadas. PluriOne CI #66 finalizó correctamente. La autenticación con correos normalizados y cuentas antiguas simuladas fue validada mediante pruebas automatizadas. En la prueba histórica del Corte 5, React respondió HTTP 200 en el puerto `5175`, pero el backend rechazó `http://127.0.0.1:5175` porque ese origen no estaba incluido en `CORS_ORIGINS`. El origen `http://127.0.0.1:5173` sí estaba autorizado. Para habilitar el origen alternativo es necesario agregarlo a `CORS_ORIGINS` y reiniciar la API. Continúan pendientes pruebas automatizadas de navegador, accesibilidad y validación del despliegue actualizado; no se considera una certificación de producción.
