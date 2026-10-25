# Validación de instalación desde clon nuevo — Cuarto corte

## 1. Identificación

- Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial.
- Responsable: Diego Rivera Aguilar.
- Fecha de la prueba: 25 de octubre de 2026.
- Commit probado: `1f7208a` (`main`, Pull Request #25).
- Alcance: reproducibilidad de clonación, construcción, arranque y comunicación CORS.
- Estado: instalación de servicios satisfactoria, con limitaciones descritas.

## 2. Preparación y aislamiento

Se clonó `main` desde GitHub en la carpeta temporal
`PluriOne-README-Limpio-1253`, fuera del proyecto original.
Se comprobó el commit, la limpieza inicial del árbol y la presencia
de README, Dockerfile, Compose, archivos de ejemplo y dependencias.
El clon no incluía archivos `.env` privados.

Se crearon variables de entorno exclusivas de la prueba:
contraseña aleatoria de PostgreSQL, clave JWT aleatoria
y valores ficticios de SMTP y Groq. No se publicaron secretos.

Los puertos habituales `8000`, `5173` y `5433` ya estaban
ocupados por otras instancias de PluriOne. Para no interrumpirlas,
se preparó dentro del clon una copia no versionada de Compose,
`docker-compose.readme-isolated.yml`, con puertos alternativos:

- PostgreSQL: `127.0.0.1:5435`.
- FastAPI: `127.0.0.1:8002`.
- React/Vite: `127.0.0.1:5175`.
- Proyecto Docker independiente: `plurione_readme_1253`.

Esta adaptación conserva los servicios y volúmenes de otros proyectos,
pero significa que la ejecución no siguió literalmente los puertos
del README sin ajustes.

## 3. Procedimiento y resultados observados

Se validó la configuración con `docker compose config --quiet`.
Los servicios `db`, `api` y `frontend` aparecieron correctamente.

La construcción e inicio se realizaron con Docker Compose usando
el nombre de proyecto aislado y la configuración derivada.
Los tres contenedores iniciaron. PostgreSQL 16 alcanzó el estado
saludable y `pg_isready` confirmó disponibilidad.

- `GET http://127.0.0.1:8002/openapi.json`: HTTP 200.
- `GET http://127.0.0.1:5175/`: HTTP 200.
- Esquema PostgreSQL: se encontraron `users`, `anomaly_logs`,
  `pipelines` y `auth_rate_limits` (4 tablas principales).
- Docker creó red y volumen independientes para el proyecto de prueba.
- El repositorio original permaneció limpio y sincronizado.

Docker reutilizó capas de imágenes que ya estaban en caché.
Por tanto, esta prueba demuestra el arranque desde un clon nuevo,
pero no una reconstrucción integral sin caché ni conexión previa.

## 4. Comprobación de CORS

Se ejecutaron solicitudes OPTIONS a `/login/` en la API aislada:

- Origen `http://127.0.0.1:5173`: HTTP 200; cabecera
  `Access-Control-Allow-Origin` coincidente.
- Origen `http://127.0.0.1:5175`: HTTP 400; origen no autorizado.

El rechazo del puerto alternativo es coherente con la lista
de orígenes explícitos de `backend/app/main.py`.
No constituye una regresión del puerto documentado.
Sin embargo, impide demostrar desde el navegador la sesión
React–FastAPI con la interfaz de esta prueba en `5175`.
No se debilitó la política CORS para ocultar esta limitación.

## 5. Alcance y limitaciones

- La prueba confirmó instalación y disponibilidad de componentes,
  no un inicio de sesión completo desde el frontend alternativo.
- Se emplearon variables falsas de SMTP y Groq; no se verificó
  el envío de correos ni una respuesta del proveedor de IA.
- No se ejecutaron pruebas automatizadas de navegador ni de carga.
- No se probó restaurar una copia de seguridad ni esquemas heredados.
- Los contenedores y el volumen aislados no se eliminaron
  durante estas comprobaciones.

La prueba funcional de pipeline, envío HTTP 201, creación de una
anomalía y alerta visual ya está documentada por separado en
[`PRUEBA_E2E_CORTE4.md`](PRUEBA_E2E_CORTE4.md).
En conjunto aportan evidencia de arranque y de integración,
sin afirmar una certificación de producción.

## 6. Conclusión

Se verificó satisfactoriamente que el repositorio integrado en
`1f7208a` puede clonarse, configurar variables privadas de prueba,
construir e iniciar PostgreSQL, FastAPI y React, y generar las tablas
principales en un entorno Docker independiente. La diferencia
respecto al README fue el uso de puertos alternativos para
evitar conflictos con instalaciones existentes.

La política CORS funcionó como está configurada para el puerto
normal `5173`; el puerto `5175` requeriría una autorización
explícita antes de usarlo para una sesión funcional. Esta
limitación se mantiene documentada para futuras verificaciones.
