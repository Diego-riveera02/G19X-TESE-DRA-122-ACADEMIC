# PluriOne — Plataforma de Observabilidad de Datos con Inteligencia Artificial

**Proyecto académico · Documentación del MVP basada en `main` en `305f2bd` (PR #16) e incluye la centralización de Axios de esta revisión (octubre de 2026).**

PluriOne es un prototipo de observabilidad de datos construido con FastAPI, PostgreSQL y React. Recibe métricas por API autenticada o desde un simulador, clasifica los eventos, conserva las anomalías relevantes, las presenta en un dashboard y ofrece consultas y diagnósticos orientativos a través de J.A.R.V.I.S. 2.0, integrado con Groq.

**Alcance del MVP:** la ingesta por JWT o clave de pipeline está implementada. El proyecto no incluye conectores permanentes a AWS ni monitoreo de infraestructura empresarial productiva. J.A.R.V.I.S. propone hipótesis de investigación; no certifica causas raíz.

## 1. Funcionalidades implementadas

- **Identidad:** registro, verificación por correo SMTP, reenvío de códigos, inicio de sesión JWT, recuperación de contraseña y rechazo de cuentas inexistentes o inactivas. Los códigos temporales tienen un propósito específico, vencen después de 10 minutos y admiten hasta cinco intentos.
- **Ingesta autenticada:** `POST /metricas/` recibe métricas con JWT y `POST /metricas/externas/` las recibe con `X-Pipeline-Key`. El servidor valida los datos y los procesa mediante una función compartida de registro y clasificación.
- **Administración de pipelines:** creación, listado, rotación y revocación mediante FastAPI y la pantalla React `frontend/src/Pipelines.jsx`. Las claves se almacenan como hash y se muestran al emitirlas o rotarlas. La copia mediante navegador requiere comprobación manual.
- **Simulador:** un proceso asíncrono en FastAPI genera métricas de demostración aproximadamente cada 30 segundos para usuarios activos, reutilizando la función que procesa la ingesta. La periodicidad no es una garantía de tiempo real estricto.
- **Persistencia de anomalías:** PostgreSQL guarda las anomalías que requieren seguimiento. Las mediciones clasificadas como normales no se persisten como anomalías en el flujo actual.
- **Dashboard:** React y Recharts muestran indicadores de latencia, calidad de datos y fallos, con alertas recibidas mediante WebSocket autenticado y segmentado por usuario.
- **Cliente HTTP:** `frontend/src/api.js` añade JWT a peticiones protegidas mediante un interceptor Axios y centraliza la limpieza de sesión ante HTTP 401, sin redirigir por errores del login o la recuperación pública.
- **Historial reversible:** consulta de anomalías activas o archivadas, archivado lógico y restauración, siempre con JWT y filtrado por usuario. La API pagina las consultas; la interfaz puede mostrar solo una parte del historial cuando hay más registros.
- **J.A.R.V.I.S. 2.0:** asistente en español con Groq, contexto reciente limitado y función de consulta controlada por FastAPI. Puede contar anomalías y recuperar hasta 10 registros recientes del usuario, filtrados por estado.
- **Presentación y reportes:** respuestas Markdown con tablas desplazables, botón «↓ Último», guía de bienvenida y exportación PDF de los registros cargados en la interfaz.

Las recomendaciones asociadas a los eventos del simulador se generan mediante reglas o textos locales: **no se invoca Groq por cada métrica**. Groq se utiliza para el chat y sus herramientas autorizadas.

## 2. Arquitectura y tecnologías

- **Backend:** Python 3.12 en la imagen documentada, FastAPI, SQLAlchemy, endpoints HTTP, autenticación JWT y WebSocket.
- **Base de datos:** PostgreSQL para usuarios, anomalías y los registros requeridos por las funciones de autenticación y pipelines.
- **Frontend:** React, Vite, React Router, Axios, Recharts, `react-markdown` y `remark-gfm`.
- **PDF:** jsPDF y jspdf-autotable.
- **Inteligencia artificial:** Groq; el prototipo documenta el identificador de modelo `openai/gpt-oss-20b`. Ese nombre no constituye evidencia de una segunda integración independiente con la API de OpenAI.
- **Contenedores:** Docker Compose; la imagen de frontend usa Node.js 22 Alpine.
- **CI actual:** GitHub Actions utiliza Python 3.12 y Node.js 22. Ejecuta las 41 pruebas aisladas del backend, ESLint y compilación de React en las ramas configuradas, incluida `main`. Las dos verificaciones del PR #15 fueron exitosas.

**Flujo de datos:** simulador **o** cliente de ingesta autenticado → validación y clasificación en FastAPI → almacenamiento de anomalías en PostgreSQL → evento WebSocket del usuario → dashboard React. J.A.R.V.I.S. consulta información del usuario únicamente a través de herramientas autorizadas del backend.

## 3. Requisitos previos

Para un entorno local se requieren Git, Docker Desktop con Docker Compose y credenciales privadas para PostgreSQL. Si se ejecutan los componentes fuera de Docker, también se necesitan Python, PostgreSQL accesible, Node.js y npm compatibles con las dependencias del proyecto. Las funciones de identidad requieren SMTP; el asistente requiere una clave API de Groq.

## 4. Configuración y seguridad de variables de entorno

El proyecto distingue dos archivos privados, que deben crearse **solamente si todavía no existen**:

- **Raíz:** copiar `.env.example` a `.env` y definir `POSTGRES_PASSWORD`.
- **Backend:** copiar `backend/.env.example` a `backend/.env` y configurar `DATABASE_URL`, `SECRET_KEY`, `SENDER_EMAIL`, `SENDER_PASSWORD` y `GROQ_API_KEY` según el entorno.

En una instalación nueva, desde PowerShell y en la raíz:

```powershell
Copy-Item .env.example .env
Copy-Item backend/.env.example backend/.env
```

Editar después ambos archivos con valores privados. **No ejecutar las copias si ya existen archivos `.env` configurados.** `DATABASE_URL` necesita un host/puerto apropiados: dentro de Compose el servicio de PostgreSQL es `db`, mientras que fuera del contenedor se utiliza la dirección accesible desde Windows. Compose construye la conexión para su entorno usando su configuración de PostgreSQL.

No compartir `.env`, claves JWT, claves de pipeline reales ni contraseñas en GitHub, capturas o ZIP de entrega. `.env.example` solo debe contener nombres y valores ficticios. Si una clave privada fue expuesta, se debe rotar; cambiar `POSTGRES_PASSWORD` en `.env` no cambia por sí mismo una contraseña ya establecida en un volumen existente.

### Controles implementados

- Los endpoints privados verifican JWT y usuario activo; el backend filtra las anomalías y eventos WebSocket por cuenta.
- Los códigos de verificación y recuperación utilizan HMAC y `hmac.compare_digest` (`backend/app/verification_codes.py`).
- **Mecanismo diferente:** las claves de pipeline se resumen con SHA-256 y se validan con `hmac.compare_digest` (`backend/app/pipeline_keys.py`). No describir estas claves como si usaran el mismo HMAC de los códigos.
- La recuperación de cuenta evita revelar en su respuesta pública si un correo está registrado, según el comportamiento implementado y cubierto por pruebas aisladas.
- Se aplican controles de intentos y límites a solicitudes sensibles. Los endpoints de ingesta tienen un límite de 60 solicitudes por minuto por origen y por usuario o pipeline, según la ruta. Cada usuario puede conservar hasta 20 pipelines activos; al intentar superar ese máximo, la API responde HTTP 409. El chat admite hasta seis solicitudes por minuto por usuario. Estas políticas tienen pruebas aisladas, pero aún requieren pruebas de carga y despliegue.
- J.A.R.V.I.S. utiliza funciones backend permitidas; no ejecuta consultas SQL arbitrarias ni acciones correctivas sobre infraestructura externa.

Estos controles forman parte de la seguridad del MVP. Una evaluación de seguridad para producción y pruebas de carga siguen fuera de las validaciones completadas.

## 5. Instalación y ejecución con Docker Compose

### 5.1. Clonar y preparar el proyecto

```powershell
git clone https://github.com/Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC.git
cd G19X-TESE-DRA-122-ACADEMIC
```

Preparar las variables indicadas en la sección 4, sin sobrescribir archivos privados existentes.

### 5.2. Iniciar API y PostgreSQL

Desde la raíz:

```powershell
docker compose up -d --build api
docker compose ps
docker compose logs --tail 40 api
```

La configuración incluye `healthcheck` con `pg_isready` en PostgreSQL y dependencia de la API respecto de una base saludable. La documentación de FastAPI está disponible normalmente en `http://127.0.0.1:8000/docs`. El despliegue descrito es **de desarrollo/demostración**, no una configuración empresarial endurecida; el Dockerfile del backend utiliza recarga de desarrollo.

### 5.3. Ejecutar el frontend

Desde la raíz, con Node.js y npm instalados:

```powershell
npm --prefix ./frontend install
npm --prefix ./frontend run dev
```

Para comprobar la compilación de React:

```powershell
npm --prefix ./frontend run build
```

También existe un Dockerfile del frontend con Node.js 22 Alpine. Se documentó la construcción local con `docker compose build frontend`, pero esa construcción no reemplaza una prueba funcional completa del navegador. La configuración Docker del frontend todavía ejecuta el servidor de desarrollo y necesita revisión antes de considerarse un despliegue de producción.

### 5.4. Direcciones utilizadas en las pruebas locales

- Frontend: `http://127.0.0.1:5173/app`
- API: `http://127.0.0.1:8000`
- Documentación de la API: `http://127.0.0.1:8000/docs`
- PostgreSQL desde el host Windows, según el Compose documentado: `127.0.0.1:5433`
- PostgreSQL entre contenedores: `db:5432`

Los puertos dependen de la configuración local. La API y WebSocket se centralizaron en `frontend/src/api.js` mediante `VITE_API_URL`. Existe `frontend/.env.example` con la dirección local de ejemplo.

## 6. Ejecución sin Docker y conservación de datos

Con PostgreSQL accesible y los archivos de entorno configurados:

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

En otra terminal, dentro de `frontend/`:

```powershell
npm install
npm run dev
```

### Esquema y migraciones

SQLAlchemy crea tablas faltantes al iniciar la aplicación. `backend/app/schema_migrations.py` aplica automáticamente a PostgreSQL las actualizaciones de autenticación para `codigo_expira_en`, `codigo_intentos` y `codigo_proposito` cuando corresponden. Este módulo **no** migra las columnas de archivado lógico.

**Archivado lógico:** el archivo `backend/migrations/001_archivado_logico_anomalias.sql` incorpora `archived` y `archived_at` a una tabla `anomaly_logs` existente. **Este SQL no se ejecuta automáticamente al iniciar la API.** Las bases nuevas creadas a partir del modelo actual ya incluyen esas columnas; una base anterior al archivado debe revisar su esquema y aplicar la migración pendiente de forma controlada, con respaldo previo. El archivo SQL no es idempotente: no debe ejecutarse si las columnas ya existen. Sigue pendiente validar la instalación completa con una base nueva y una base antigua, sin pérdida de datos.

El volumen PostgreSQL usado por Docker Compose debe conservarse. Para detener los servicios sin borrar sus datos:

```powershell
docker compose stop
```

**No ejecutar `docker compose down -v` ni eliminar el volumen** cuando se necesite conservar la información. El archivado lógico tampoco sustituye un respaldo de la base de datos.

## 7. Uso de la plataforma y API de ingesta

### 7.1. Flujo desde React

1. Registrarse y verificar la cuenta con el código de correo; iniciar sesión.
2. Abrir el dashboard y observar las métricas y alertas de demostración recibidas por WebSocket.
3. Consultar a J.A.R.V.I.S.: «¿Cuántas anomalías críticas tengo y cuál fue la más reciente?». Distinguir siempre los datos recuperados de las hipótesis generadas.
4. Consultar el historial, archivar con confirmación, restaurar cuando corresponda y exportar los registros visibles en PDF.
5. Para recuperar el acceso, solicitar el código desde el formulario React, validarlo y establecer una contraseña nueva.

La memoria conversacional es temporal y limitada; no persiste entre sesiones.

### 7.2. Endpoints de ingesta y pipelines

| Método | Ruta | Acceso |
| --- | --- | --- |
| `POST` | `/metricas/` | JWT del usuario |
| `POST` | `/metricas/externas/` | Cabecera `X-Pipeline-Key` |
| `POST` | `/pipelines/` | JWT del usuario |
| `GET` | `/pipelines/` | JWT del usuario |
| `POST` | `/pipelines/{pipeline_id}/rotar/` | JWT del usuario |
| `POST` | `/pipelines/{pipeline_id}/revocar/` | JWT del usuario |

La administración de pipelines está disponible en la API y en la pantalla React. La clave se muestra al crear o rotar un pipeline; debe conservarse de forma segura. El botón de copia dispone de una alternativa de selección manual si el navegador bloquea el portapapeles.

**Ejemplo orientativo de ingesta externa (bash):**

```bash
curl -X POST 'http://127.0.0.1:8000/metricas/externas/' \
  -H 'X-Pipeline-Key: plr_EJEMPLO_NO_VALIDO' \
  -H 'Content-Type: application/json' \
  -d '{"metrica":"latencia_ms","valor":850}'
```

La clave mostrada es **ficticia e inválida**. Para una prueba real, reemplazarla por la clave emitida al crear el pipeline. Según `MetricaExternaEntrada` en `backend/app/schemas.py`, el cuerpo exige `metrica` (`latencia_ms`, `datos_corruptos_%` o `tasa_fallos_%`) y `valor` numérico entre 0 y 10000, con máximo de 100 para porcentajes. No admite propiedades extra: los datos inválidos reciben HTTP 422. El ejemplo de latencia 850 es válido como estructura, pero **no acredita por sí solo la prueba de punta a punta**; esta debe ejecutarse con una clave real y comprobarse en el dashboard.

La ingesta autenticada no implica conectores automáticos a AWS ni otros sistemas productivos. La API aplica límites de 60 solicitudes por minuto a la ingesta y una cuota de 20 pipelines activos por usuario; las pruebas aisladas cubren estas restricciones. Quedan pendientes la validación integral con PostgreSQL y las pruebas de carga.

### 7.3. Archivado y restauración

- `GET /anomalias/`: listar anomalías activas del usuario.
- `DELETE /anomalias/`: archivarlas lógicamente, sin eliminarlas físicamente.
- `GET /anomalias/archivadas/`: consultar su historial archivado.
- `POST /anomalias/restaurar/`: restaurar sus anomalías archivadas.

Estas operaciones requieren JWT y filtran los registros por usuario. La API utiliza paginación; la documentación anterior señala un límite predeterminado de hasta 100 registros por consulta, por lo que una página no equivale necesariamente a todo el historial.

## 8. Pruebas, verificaciones e integración continua

La base integrada en `305f2bd` cuenta con **58 pruebas** distribuidas en tres archivos:

| Archivo | Pruebas | Cobertura y ejecución |
| --- | ---: | --- |
| `backend/tests/test_flujos_aislados.py` | 41 | Flujos de identidad, seguridad, límites de ingesta, chat, WebSocket y pipelines con SQLite aislado. **Se ejecutan en CI.** |
| `backend/tests/test_integracion_http.py` | 9 | Pruebas HTTP y disponibilidad de API, frontend, CORS y PostgreSQL. **No se ejecutan en el CI actual.** |
| `backend/tests/test_seguridad_archivado.py` | 8 | Rechazo de accesos no autorizados y rutas de historial. **No se ejecutan en el CI actual.** |

En el corte actual, las **41 pruebas aisladas** aprobaron localmente y el PR #15 obtuvo dos verificaciones exitosas en GitHub Actions. Las nueve pruebas HTTP y las ocho de seguridad/archivado aprobaron en ejecuciones locales anteriores del 23 de octubre de 2026, pero **no se han vuelto a ejecutar todas juntas tras los últimos cambios**. No debe confundirse el total de pruebas disponibles con una validación integral en un solo proceso.

### Ejecución local

Para ejecutar exclusivamente las pruebas HTTP, con API, React y PostgreSQL levantados y configurados, utilizar el archivo `backend/tests/test_integracion_http.py` según sus requisitos. El comando amplio siguiente descubre las distintas suites y **puede requerir preparación adicional de servicios/entornos**, por lo que no se presenta como una validación que ya haya pasado completa:

```powershell
python -m unittest discover -s backend/tests -p "test_*.py" -v
```

Para el frontend:

```powershell
npm --prefix ./frontend run build
```

### GitHub Actions

El workflow `.github/workflows/ci.yml` ejecuta las 41 pruebas aisladas con Python 3.12 y SQLite en memoria. El trabajo de frontend utiliza Node.js 22, `npm ci`, `npm run lint` y `npm run build`. Los dos trabajos aprobaron las verificaciones del Pull Request #15.

**Cobertura pendiente:** incorporar las 17 pruebas HTTP y de archivado al CI con servicios apropiados, añadir pruebas completas de navegador, carga y seguridad, y verificar migraciones en instalaciones nuevas y antiguas. El lint y la ejecución del workflow en `main` están configurados.

**Antecedentes de verificación local:** se reportaron arranque de FastAPI y PostgreSQL, `/docs` con HTTP 200, compilación de Vite, pruebas de acceso con JWT, recuperación mediante SMTP y funcionamiento del chat/WebSocket. Esas comprobaciones corresponden a distintas sesiones de desarrollo, no a una campaña integral de pruebas de producción.

## 9. Limitaciones, riesgos y uso de IA

- El simulador usa telemetría sintética y la API puede aceptar entradas externas autenticadas; no hay prueba de monitoreo continuo en AWS ni de integración automática con sistemas corporativos.
- La interfaz permite administrar pipelines y utiliza URL, token JWT y respuesta HTTP 401 centralizados en `api.js` para peticiones Axios. Continúan pendientes las pruebas completas de navegador y la modularización adicional de componentes grandes.
- Los límites de ingesta y cuota de pipelines están implementados y cubiertos por pruebas aisladas; no se han realizado pruebas completas de seguridad, carga, resiliencia, accesibilidad, alta disponibilidad ni una puesta en producción certificada.
- La exportación PDF contiene los registros cargados en la interfaz, no necesariamente todo el histórico almacenado en PostgreSQL.
- J.A.R.V.I.S. puede equivocarse; sus recomendaciones no sustituyen la investigación técnica. No inspecciona logs, CPU, red ni infraestructura empresarial por sí solo, y no ejecuta remediación automática.
- Las dependencias de Groq y SMTP están sujetas a disponibilidad y límites de sus proveedores.
- Las imágenes Docker siguen orientadas a desarrollo/demostración. Falta comprobar el proceso de migración de archivado con volúmenes nuevos y antiguos sin pérdida de datos.

### Transparencia sobre inteligencia artificial

Para el MVP académico se integró **Groq** como proveedor de inferencia del asistente J.A.R.V.I.S. 2.0, con una API que permite generar respuestas y coordinar herramientas de consulta autorizadas en FastAPI. Esta decisión implementa el flujo conversacional previsto sin incorporar Azure OpenAI Service, Azure AI Search, Microsoft Purview ni Azure Monitor, que figuran en la propuesta empresarial pero **no forman parte de este prototipo**. La sustitución no significa equivalencia funcional con esos servicios ni demuestra una ventaja de costo o rendimiento. La justificación técnica debe contrastarse con la decisión y aceptación del equipo y del profesor; no se afirma una aprobación formal no documentada.

Durante el desarrollo se utilizó **asistencia de IA generativa** para analizar problemas, proponer cambios y mejorar la documentación. El equipo conserva la responsabilidad sobre las decisiones, el código y la verificación de pruebas; las respuestas generadas no sustituyen la evidencia de ejecución.

## 10. Documentación y pendientes principales

- [`docs/PRD.md`](docs/PRD.md): objetivos, requisitos funcionales y criterios de aceptación.
- [`docs/MVP.md`](docs/MVP.md): alcance, estado verificable y exclusiones.
- [`frontend/README.md`](frontend/README.md): instalación e interfaz React.
- `docs/Informe Técnico Plataforma de Observabilidad.pdf` y `docs/Bitácora de Desarrollo Ágil (Scrum) - Proyecto PluriOne.pdf`: documentos empresariales y académicos de referencia, sujetos a disponibilidad en la entrega.

### Lista de verificación

- [x] Autenticación JWT, SMTP, recuperación y códigos protegidos mediante HMAC.
- [x] Simulador automático e ingesta por JWT o clave de pipeline en la API.
- [x] Alta, listado, rotación y revocación de pipelines desde el backend.
- [x] Dashboard, WebSocket por usuario, archivado/restauración, chat controlado y PDF.
- [x] CI con 41 pruebas aisladas, ESLint y compilación de React, con verificaciones satisfactorias del PR #15.
- [x] Pantalla React de pipelines, centralización de `VITE_API_URL` y archivo `frontend/.env.example`.
- [x] Interceptores Axios para añadir JWT solo a rutas privadas y cerrar sesiones rechazadas con HTTP 401; falta comprobar el flujo real en navegador.
- [x] Extracción de rutas a `pipelines_router.py`, `chat_router.py`, `metricas_router.py` y `websocket_router.py`, además del router de anomalías. La autenticación aún permanece en `main.py`.
- [x] Límites de ingesta y chat y máximo de 20 pipelines activos por usuario, con pruebas aisladas.
- [x] ESLint y compilación configurados en CI para `main`. Las 17 pruebas HTTP/archivado aprobaron previamente de forma local; sigue pendiente integrarlas en CI con los servicios correspondientes y repetirlas en la versión actual.
- [ ] Verificar migración de archivado en instalaciones nuevas y antiguas, y realizar una instalación limpia completa con evidencia reproducible.
- [ ] Preparar contenedores adecuados para producción, evidencias y revisión de seguridad de secretos/ZIP.
- [ ] Conectores a fuentes productivas y remediación automática, fuera del alcance demostrado.

**Estado documental:** actualización de la base `305f2bd` (PR #16) con centralización de Axios incluida en esta revisión. Persisten pruebas de instalación limpia, migración de archivado, navegador y PostgreSQL completo; la entrega sigue siendo un MVP académico, no una certificación de producción.
