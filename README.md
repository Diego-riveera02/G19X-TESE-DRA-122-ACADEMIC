# PluriOne — Plataforma de Observabilidad de Datos con Inteligencia Artificial

**Proyecto académico · Documentación consolidada para el Corte 3 (octubre de 2026).**

PluriOne es un prototipo de observabilidad de datos construido con FastAPI, PostgreSQL y React. Recibe métricas por API autenticada o desde un simulador, clasifica los eventos, conserva las anomalías relevantes, las presenta en un dashboard y ofrece consultas y diagnósticos orientativos a través de J.A.R.V.I.S. 2.0, integrado con Groq.

**Alcance comprobado en el repositorio revisado:** existen endpoints de ingesta con JWT y clave de pipeline; **no** se ha demostrado una conexión permanente con AWS o con infraestructura empresarial productiva. El asistente propone hipótesis para investigar, no causas raíz confirmadas.

## 1. Funcionalidades implementadas

- **Identidad:** registro, verificación por correo SMTP, reenvío de códigos, inicio de sesión JWT, recuperación de contraseña y rechazo de cuentas inexistentes o inactivas. Los códigos temporales tienen un propósito específico, vencen después de 10 minutos y admiten hasta cinco intentos.
- **Ingesta autenticada:** `POST /metricas/` recibe métricas con JWT y `POST /metricas/externas/` las recibe con `X-Pipeline-Key`. El servidor valida los datos y los procesa mediante una función compartida de registro y clasificación.
- **Administración de pipelines en la API:** alta, listado, rotación y revocación de claves. La clave se muestra al crearla o rotarla; la base de datos conserva su hash SHA-256. **Todavía no existe una pantalla de administración de pipelines en React.**
- **Simulador:** un proceso asíncrono en FastAPI genera métricas de demostración aproximadamente cada 30 segundos para usuarios activos, reutilizando la función que procesa la ingesta. La periodicidad no es una garantía de tiempo real estricto.
- **Persistencia de anomalías:** PostgreSQL guarda las anomalías que requieren seguimiento. Las mediciones clasificadas como normales no se persisten como anomalías en el flujo actual.
- **Dashboard:** React y Recharts muestran indicadores de latencia, calidad de datos y fallos, con alertas recibidas mediante WebSocket autenticado y segmentado por usuario.
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
- **CI actual:** `.github/workflows/ci.yml`, con Python 3.12 y Node.js 24 en sus trabajos respectivos.

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
- Se aplican controles de intentos y limitación de solicitudes de autenticación; **todavía falta validar y fortalecer límites específicos de ingesta y cuotas de pipelines**.
- J.A.R.V.I.S. utiliza funciones backend permitidas; no ejecuta consultas SQL arbitrarias ni acciones correctivas sobre infraestructura externa.

Ninguno de estos controles sustituye una auditoría exhaustiva de seguridad de producción.

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

La configuración revisada incluye `healthcheck` con `pg_isready` en PostgreSQL y dependencia de la API respecto de una base saludable. La documentación de FastAPI está disponible normalmente en `http://127.0.0.1:8000/docs`. El despliegue documentado es **de desarrollo/demostración**, no una configuración empresarial endurecida; el Dockerfile del backend todavía utiliza recarga de desarrollo.

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

Los puertos dependen de la configuración local. **Pendiente en el frontend:** reemplazar las URL repetidas del backend por una variable `VITE_API_URL` y proporcionar `frontend/.env.example`. La existencia de esta sección no implica que esa refactorización ya se haya realizado.

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

SQLAlchemy crea tablas faltantes al iniciar la aplicación. `backend/app/schema_migrations.py` incluye migraciones documentadas para los campos de códigos `codigo_expira_en`, `codigo_intentos` y `codigo_proposito` y permite actualizar instalaciones anteriores sin perder los registros.

**Archivado lógico:** existe además `backend/migrations/001_archivado_logico_anomalias.sql`, que añade `archived` y `archived_at` a `anomaly_logs`. La migración se aplicó en el entorno de desarrollo durante una auditoría anterior; **con los cuatro documentos recibidos no se pudo confirmar que esta migración específica se ejecute automáticamente en todas las instalaciones nuevas o antiguas**. Antes de aplicarla en otro entorno, comprobar el esquema y el arranque con datos de respaldo. No volver a ejecutar manualmente un SQL sin revisar si sus columnas ya existen.

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

La administración de pipelines está disponible en la API, **no todavía en una pantalla de React**. Al crear o rotar un pipeline, copiar y resguardar la clave devuelta en ese momento; no depender de recuperarla después.

**Ejemplo orientativo de ingesta externa (bash):**

```bash
curl -X POST 'http://127.0.0.1:8000/metricas/externas/' \
  -H 'X-Pipeline-Key: plr_EJEMPLO_NO_VALIDO' \
  -H 'Content-Type: application/json' \
  -d '{"metrica":"latencia_ms","valor":850}'
```

La clave mostrada es **ficticia e inválida**. Sustituirla por la clave real emitida al crear el pipeline y confirmar el esquema exacto del cuerpo en `http://127.0.0.1:8000/docs` o `backend/app/schemas.py` antes de probarlo: el ZIP aportado contiene documentos, no código para verificar el contrato del endpoint. Por tanto, este fragmento muestra el flujo esperado, **no una ejecución validada de extremo a extremo**.

La ingesta autenticada tampoco implica la existencia de conectores automáticos a AWS u otros sistemas productivos. No está acreditado un límite de frecuencia para esas rutas ni una cuota máxima de pipelines por usuario.

### 7.3. Archivado y restauración

- `GET /anomalias/`: listar anomalías activas del usuario.
- `DELETE /anomalias/`: archivarlas lógicamente, sin eliminarlas físicamente.
- `GET /anomalias/archivadas/`: consultar su historial archivado.
- `POST /anomalias/restaurar/`: restaurar sus anomalías archivadas.

Estas operaciones requieren JWT y filtran los registros por usuario. La API utiliza paginación; la documentación anterior señala un límite predeterminado de hasta 100 registros por consulta, por lo que una página no equivale necesariamente a todo el historial.

## 8. Pruebas, verificaciones e integración continua

El repositorio revisado contiene **49 funciones de prueba** distribuidas en tres archivos:

| Archivo | Pruebas | Cobertura y ejecución |
| --- | ---: | --- |
| `backend/tests/test_flujos_aislados.py` | 32 | Flujos de identidad, seguridad, ingesta, WebSocket y pipelines con SQLite aislado. **Se ejecutan en CI.** |
| `backend/tests/test_integracion_http.py` | 9 | Pruebas HTTP y disponibilidad de API, frontend, CORS y PostgreSQL. **No se ejecutan en el CI actual.** |
| `backend/tests/test_seguridad_archivado.py` | 8 | Rechazo de accesos no autorizados y rutas de historial. **No se ejecutan en el CI actual.** |

Las nueve pruebas HTTP y las ocho de seguridad se ejecutaron satisfactoriamente en revisiones anteriores (17 en total); **no debe interpretarse ese resultado histórico como una ejecución reciente de las 49**.

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

El workflow `.github/workflows/ci.yml` instala dependencias de Python 3.12 y ejecuta 32 pruebas aisladas con SQLite en memoria. Para React usa Node.js 24, `npm ci` y `npm run build`, sin requerir los archivos `.env` privados. Se verificó su finalización satisfactoria para el commit `f6a6ab9` en la rama `fix/segunda-auditoria-plurione`.

**Cobertura pendiente:** incorporar las otras 17 pruebas, PostgreSQL de integración, `npm run lint`, pruebas de carga, seguridad y navegador. Según la revisión del Corte 3, el workflow todavía debe configurarse para ejecutarse también en cada `push` a `main` (además de la rama de correcciones y los pull requests). La versión de Node.js en CI (24) y Docker (22) debe revisarse para alinearlas.

**Antecedentes de verificación local:** se reportaron arranque de FastAPI y PostgreSQL, `/docs` con HTTP 200, compilación de Vite, pruebas de acceso con JWT, recuperación mediante SMTP y funcionamiento del chat/WebSocket. Esas comprobaciones corresponden a distintas sesiones de desarrollo, no a una campaña integral de pruebas de producción.

## 9. Limitaciones, riesgos y uso de IA

- El simulador usa telemetría sintética y la API puede aceptar entradas externas autenticadas; no hay prueba de monitoreo continuo en AWS ni de integración automática con sistemas corporativos.
- La interfaz aún no permite administrar pipelines. También faltan centralizar la URL de FastAPI y modularizar los archivos grandes del frontend y backend.
- No se han demostrado cuotas para ingesta/pipelines, pruebas completas de seguridad, carga, resiliencia, accesibilidad, alta disponibilidad ni una puesta en producción certificada.
- La exportación PDF contiene los registros cargados en la interfaz, no necesariamente todo el histórico almacenado en PostgreSQL.
- J.A.R.V.I.S. puede equivocarse; sus recomendaciones no sustituyen la investigación técnica. No inspecciona logs, CPU, red ni infraestructura empresarial por sí solo, y no ejecuta remediación automática.
- Las dependencias de Groq y SMTP están sujetas a disponibilidad y límites de sus proveedores.
- Las imágenes Docker siguen orientadas a desarrollo/demostración. Falta comprobar el proceso de migración de archivado con volúmenes nuevos y antiguos sin pérdida de datos.

### Transparencia sobre inteligencia artificial

El backend utiliza **Groq**, mientras que la revisión académica identifica **Azure** como tecnología contemplada en una propuesta anterior. No se identificó una integración Azure en el código revisado; la justificación y aceptación formal de la alternativa deben confirmarse con el profesor o la empresa. No se atribuyen beneficios de costo, rendimiento o aprobación sin evidencia.

Durante el desarrollo y la auditoría se utilizó **asistencia de IA generativa** para analizar problemas, proponer cambios y revisar documentación. El equipo sigue siendo responsable del código, las decisiones y la verificación de pruebas: ninguna respuesta generada por IA constituye, por sí sola, evidencia de funcionamiento.

## 10. Documentación y pendientes principales

- [`docs/PRD.md`](docs/PRD.md): objetivos, requisitos funcionales y criterios de aceptación.
- [`docs/MVP.md`](docs/MVP.md): alcance, estado verificable y exclusiones.
- [`frontend/README.md`](frontend/README.md): instalación e interfaz React.
- `docs/Informe Técnico Plataforma de Observabilidad.pdf` y `docs/Bitácora de Desarrollo Ágil (Scrum) - Proyecto PluriOne.pdf`: documentos referidos en la documentación previa; su contenido no formó parte del ZIP revisado.

### Lista de verificación

- [x] Autenticación JWT, SMTP, recuperación y códigos protegidos mediante HMAC.
- [x] Simulador automático e ingesta por JWT o clave de pipeline en la API.
- [x] Alta, listado, rotación y revocación de pipelines desde el backend.
- [x] Dashboard, WebSocket por usuario, archivado/restauración, chat controlado y PDF.
- [x] CI con 32 pruebas aisladas y compilación de React, con ejecución satisfactoria documentada.
- [ ] Pantalla de pipelines en React, centralización de `VITE_API_URL` y `frontend/.env.example`.
- [ ] Modularización de archivos principales y consolidación de límites de solicitudes.
- [ ] Integrar pruebas HTTP/archivado, lint, PostgreSQL y ejecución del CI en `main`.
- [ ] Verificar migración de archivado en instalaciones nuevas y antiguas, y realizar una instalación limpia completa con evidencia reproducible.
- [ ] Preparar contenedores adecuados para producción, evidencias y revisión de seguridad de secretos/ZIP.
- [ ] Conectores a fuentes productivas y remediación automática, fuera del alcance demostrado.

**Estado documental:** consolidación de los cuatro Markdown recibidos para el tercer corte, basada en la versión `b5957d4`. Los cambios en la aplicación o la base de datos quedan fuera de esta entrega documental.
