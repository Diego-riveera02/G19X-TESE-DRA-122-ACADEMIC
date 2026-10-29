# Informe de instalación desde un clon limpio — Corte 5

**Proyecto:** PluriOne — Plataforma de Observabilidad de Datos con Inteligencia Artificial
**Tipo de evidencia:** Validación académica de instalación, funcionamiento y recuperación del entorno
**Fecha de las pruebas:** 27 de octubre de 2026
**Repositorio:** [Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC](https://github.com/Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC)
**Rama y commit evaluados:** `main` — `98dfdd6`
**Sistema anfitrión:** Windows, PowerShell, Docker Desktop y Docker Compose

## 1. Objetivo y alcance

Comprobar, desde una descarga nueva del repositorio de GitHub, que el proyecto PluriOne se puede configurar e iniciar siguiendo las instrucciones de su `README.md`, con PostgreSQL, FastAPI, React y el servicio de correo de pruebas Mailpit. Validar también el registro y verificación de una cuenta ficticia, la recuperación de contraseña y el acceso al Dashboard. Finalmente, restaurar la instalación de trabajo sin eliminar su base de datos ni alterar sus archivos versionados.

La prueba se efectuó como instalación **aislada y de desarrollo**, no como certificación para producción. Se utilizaron los puertos documentados por el README tras detener temporalmente los servicios originales. La separación entre proyectos se consiguió mediante una variable privada adicional de Docker Compose, medida que se declara expresamente para no presentar el ensayo como una instalación sin ajustes del entorno.

## 2. Referencia técnica revisada

Se revisaron las 344 líneas del `README.md` y la configuración `docker-compose.yml` (54 líneas). Se verificó la presencia de los archivos versionados `README.md`, `.env.example`, `backend/.env.example`, `frontend/.env.example`, `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `backend/requirements.txt` y `frontend/package.json`.

La pila utilizada fue:

| Elemento | Tecnología o servicio |
| --- | --- |
| API y autenticación | Python, FastAPI y JWT |
| Persistencia | PostgreSQL 16 |
| Interfaz | React y Vite |
| Contenedores | Docker Compose |
| Correo local | Mailpit, perfil opcional `correo-local` |
| IA conversacional | Integración Groq opcional; no probada con clave real en este clon |

## 3. Clonación desde GitHub

Se creó en el Escritorio una carpeta separada denominada `PluriOne_Instalacion_Literal_Corte5` y dentro de ella se ejecutó la clonación indicada por el README:

```powershell
git clone https://github.com/Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC.git
cd G19X-TESE-DRA-122-ACADEMIC
```

Las verificaciones de Git confirmaron que el clon y el repositorio original apuntaban al mismo commit `98dfdd6`, con rama `main` y árbol de trabajo limpio. El clon no contenía `.env`, `backend/.env` ni `frontend/.env` privados; los patrones correspondientes estaban protegidos por `.gitignore`.

## 4. Configuración privada e independencia de datos

Se prepararon los archivos privados `.env` y `backend/.env` del clon utilizando las plantillas públicas, sin copiar credenciales del entorno original. Se generaron una contraseña de PostgreSQL y una clave JWT nuevas mediante un generador criptográfico de números aleatorios. No se imprimieron ni se incorporan al informe.

En el archivo `.env` del clon se añadió:

```dotenv
COMPOSE_PROJECT_NAME=plurione_corte5_literal
```

Se configuró Mailpit en `backend/.env` con `SMTP_SERVER=mailpit`, `SMTP_PORT=1025`, `SMTP_STARTTLS=false` y `SMTP_AUTH=false`, además de un remitente ficticio. Se conservaron los orígenes CORS documentados para el puerto 5173. No se utilizó ninguna clave real de Groq.

Los proyectos Docker quedaron identificados así:

| Elemento | Instalación original | Instalación del Corte 5 |
| --- | --- | --- |
| Nombre del proyecto Compose | `g19x-tese-dra-122-academic` | `plurione_corte5_literal` |
| Volumen PostgreSQL | `g19x-tese-dra-122-academic_plurione_postgres_data` | `plurione_corte5_literal_plurione_postgres_data` |

La inspección de los montajes del contenedor PostgreSQL confirmó que los volúmenes eran diferentes. Antes de arrancar el clon se comprobó que no existían contenedores ni volúmenes etiquetados con el nombre nuevo. Se validó la configuración mediante `docker compose config --quiet`.

## 5. Construcción e inicio según el README

La instalación original ya utilizaba los puertos `5173`, `8000` y `5433`. Para evitar conflictos, se verificaron sus contenedores y su volumen y después se detuvieron **temporalmente** los servicios `frontend`, `api` y `db`, sin eliminarlos.

Desde la carpeta raíz del clon se ejecutaron los comandos:

```powershell
docker compose --profile correo-local build
docker compose --profile correo-local up -d --build
docker compose --profile correo-local ps
```

Docker completó la construcción de las imágenes y creó la red, el volumen y los cuatro servicios del proyecto aislado. PostgreSQL alcanzó el estado `healthy` y se comprobó por inspección de Docker que usaba el volumen `plurione_corte5_literal_plurione_postgres_data`.

| Servicio | Comprobación | Resultado observado |
| --- | --- | --- |
| FastAPI | `http://127.0.0.1:8000/docs` | HTTP 200 |
| Frontend | `http://127.0.0.1:5173/` | HTTP 200 |
| Mailpit | `http://127.0.0.1:8025/` | HTTP 200 |
| PostgreSQL | Estado de salud del contenedor | `healthy` |

La prueba conservó los mismos puertos del README. La necesidad de detener el entorno original y definir el nombre exclusivo de Compose constituye una **adaptación de entorno documentada**.

## 6. Verificación funcional de identidad y acceso

### 6.1. Registro y activación

En una ventana privada del navegador se utilizó la interfaz React para registrar una cuenta ficticia de prueba con nombre **Prueba Corte 5** y correo `prueba.corte5@example.com`. Se recibió en Mailpit un mensaje de verificación y se completó el procedimiento de activación desde la aplicación.

Una consulta de solo lectura en PostgreSQL confirmó exactamente una cuenta con el correo indicado y el campo `is_active` en valor verdadero (`t`). No se copiaron contraseñas ni códigos de verificación a este archivo.

### 6.2. Incidencia inicial de autenticación

El primer flujo de inicio de sesión presentó una incidencia: las solicitudes `POST /login/` devolvieron **HTTP 401 Unauthorized**. El formulario React mostró el mensaje «Correo o contraseña incorrectos».

Se investigó sin modificar datos. Se confirmó que el correo coincidía exactamente en la tabla `users`, que la cuenta estaba activa, que React enviaba un formulario `application/x-www-form-urlencoded` con campos `username` y `password`, y que el backend empleaba el mismo contexto `passlib`/bcrypt para generar y verificar las contraseñas. Con estas comprobaciones **no se determinó la causa exacta** del rechazo inicial; no se atribuye el problema a un componente sin evidencia.

**Seguimiento del Corte 6:** después de publicar la normalización de correos en `3cbc283`, se registró una nueva prueba funcional de registro, verificación e inicio de sesión en un clon aislado actualizado. El primer login funcionó sin recuperar la contraseña. El HTTP 401 histórico no volvió a reproducirse en esa prueba; sin embargo, su causa original no quedó demostrada. No se atribuye con certeza a diferencias de mayúsculas o espacios en el correo. La evidencia se documenta en `EVIDENCIAS_FUNCIONALES_CORTE6.md`.

**Seguimiento adicional del 29 de octubre de 2026:**

Se reviso nuevamente la incidencia original y se
comparo la implementacion anterior de autenticacion
con la correccion de normalizacion de correos.

En el commit 98dfdd6, el inicio de sesion utilizaba
una comparacion exacta del correo almacenado.

La correccion del commit 3cbc283 incorporo la
normalizacion mediante LOWER, TRIM y normalizar_correo.

Una consulta SQL de solo lectura, utilizando un correo
ficticio con diferencias de mayusculas y espacios,
obtuvo los siguientes resultados:

- Busqueda exacta anterior: NO_ENCONTRADO.
- Busqueda normalizada: ENCONTRADO.

Esta prueba reprodujo un mecanismo que podia impedir
localizar usuarios en la implementacion anterior.

Adicionalmente, se ejecutaron tres pruebas aisladas
de autenticacion y todas aprobaron.

En el entorno local principal se registro y verifico
una cuenta nueva mediante React y Mailpit.

El primer inicio de sesion funciono sin recuperar
la contrasena y la solicitud POST /login/ devolvio
HTTP 200. Tambien se comprobo el acceso al Dashboard.

La evidencia visual se publico en el commit 9b5a4e3.

El analisis tecnico reproducible se documento y
publico en el commit 6a6bf0c.

**Limitacion:** la incidencia historica no se
reprodujo nuevamente con sus condiciones originales.
La bitacora del Corte 5 registro que se habia
comprobado la coincidencia del correo en la base
de datos. Por ello, la prueba de normalizacion
no demuestra que las diferencias de mayusculas
o espacios causaran aquel HTTP 401.

Se conserva esta limitacion para distinguir el
mecanismo reproducido de la causa historica,
que continua sin determinarse con certeza.

El desarrollo completo de la investigacion se
encuentra en [EVIDENCIAS_FUNCIONALES_CORTE6.md](EVIDENCIAS_FUNCIONALES_CORTE6.md).

### 6.3. Recuperación de contraseña

Se inició la recuperación desde React para el usuario de prueba. Mailpit recibió un correo con código temporal. Tras introducir el código y una contraseña nueva, la aplicación permitió actualizar la contraseña. Tanto el código como la contraseña fueron omitidos de la documentación por motivos de seguridad.

### 6.4. Inicio de sesión y Dashboard

Después de la recuperación se consiguió iniciar sesión y se visualizó el Dashboard bajo el nombre de **Prueba Corte 5**. La captura de verificación mostró gráficas de latencia y calidad, indicadores de alerta y diagnósticos automáticos, con los accesos de navegación visibles.

Este resultado valida la entrada al Dashboard después de recuperar la contraseña. No demuestra por sí solo todas las rutas protegidas, el comportamiento ante expiración de JWT ni el funcionamiento completo de cada vista.

### 6.5. Validación funcional posterior del Corte 6

La prueba posterior se documentó sobre el commit `42a49d1`, utilizando el clon aislado existente del Corte 5, con PostgreSQL y Mailpit independientes del proyecto principal. No constituye una nueva instalación completamente libre de adaptaciones.

| Paso | Comprobación | Resultado documentado |
| --- | --- | --- |
| 1 | Registrar una cuenta nueva desde React | Correcto |
| 2 | Recibir el código mediante Mailpit y verificar la cuenta | Correcto |
| 3 | Iniciar sesión sin recuperar la contraseña | Correcto |
| 4 | Crear el pipeline `pipeline-corte6-latencia` | Correcto |
| 5 | Enviar `latencia_ms = 9500` mediante `/metricas/externas/` | HTTP 201 |
| 6 | Consultar el dashboard | Alerta crítica visible |
| 7 | Consultar el historial de anomalías | Registro confirmado en la fila 8 |

Estos resultados se encuentran registrados en [EVIDENCIAS_FUNCIONALES_CORTE6.md](EVIDENCIAS_FUNCIONALES_CORTE6.md), incorporado al repositorio mediante el commit `9e9bd39`.

Las credenciales, códigos de verificación, tokens JWT y claves de pipelines no se incluyen en la documentación.

**Evidencia visual pendiente:** incorporar al repositorio las capturas ya obtenidas, previamente revisadas para ocultar cualquier dato sensible.

**Limitación:** el recorrido completo se comprobó en un clon existente actualizado. La prueba no demuestra una instalación nueva desde cero sin adaptaciones ni identifica de forma concluyente la causa del HTTP 401 original.

## 7. Integración continua

Se comprobó previamente en GitHub Actions el último commit utilizado:

| Dato | Resultado |
| --- | --- |
| Commit | `98dfdd6` |
| Workflow | `PluriOne CI` |
| ID de ejecución | `40600515152` |
| Estado | `completed` |
| Conclusión | `success` |

**Enlace:** https://github.com/Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC/actions/runs/40600515152

La integración continua aprobada complementa las pruebas manuales de instalación, pero no las sustituye.

## 8. Restauración de la instalación original

Al finalizar las pruebas se ejecutó, desde el clon:

```powershell
docker compose --profile correo-local stop frontend api mailpit db
```

Se verificó que los cuatro contenedores del clon habían quedado detenidos y que su volumen continuaba existente. Después se reinició el PostgreSQL original, se esperó hasta obtener estado `healthy` y se iniciaron los contenedores originales `api` y `frontend`.

Las comprobaciones finales confirmaron:

- Identidad de los tres contenedores originales conservada.
- Nombre e identidad del volumen PostgreSQL original conservados.
- PostgreSQL original saludable.
- FastAPI original con respuesta HTTP 200 en `/docs`.
- Frontend original con respuesta HTTP 200.
- Repositorio original en `main`, sincronizado y sin cambios locales.
- Clon detenido, con su volumen y los datos de prueba conservados.

En ninguna fase se ejecutó `docker compose down -v` ni se eliminaron volúmenes. Estas comprobaciones acreditan conservación de recursos y disponibilidad del servicio; **no equivalen a una auditoría exhaustiva de integridad ni a una restauración probada de un respaldo**.

## 9. Resumen de evidencias

| Evidencia | Medio de comprobación | Estado |
| --- | --- | --- |
| Clon limpio y commit coincidente | `git rev-parse HEAD`, `git status` | Verificada |
| Plantillas y archivos privados separados | Exploración de archivos y `.gitignore` | Verificada |
| Proyecto y volumen Docker exclusivos | `docker compose config`, `docker inspect` | Verificada |
| API, frontend y Mailpit operativos | Peticiones HTTP | Verificada |
| Registro y verificación | Interfaz React y correo capturado en Mailpit | Verificada |
| Cuenta activa | Consulta SQL de solo lectura | Verificada |
| Recuperación de contraseña | Mailpit e interfaz React | Verificada |
| Inicio de sesión y Dashboard | Comprobación visual | Verificada tras recuperación |
| Primer inicio de sesión | HTTP 401 | Incidencia documentada |
| Validación posterior del Corte 6 | Login sin recuperación, pipeline y alerta | Documentada en clon aislado |
| Entorno original restaurado | Docker, HTTP y Git | Verificada |
| CI para commit evaluado | GitHub Actions | `success` |

Las capturas y las salidas de consola fueron revisadas durante la sesión de pruebas. **No están incrustadas en este archivo**: si el profesor exige capturas descargables dentro del repositorio, deberán guardarse en `docs/` con datos sensibles ocultos y enlazarse desde aquí.

## 10. Limitaciones, hallazgos y acciones recomendadas

1. **Autenticación:** investigar el HTTP 401 inicial si vuelve a reproducirse con credenciales nuevas, preservando registros de respuesta y sin publicar contraseñas.
2. **Documentación:** actualizar en el README las referencias históricas al commit `657499b` y otras descripciones que ya no representen el estado actual del Corte 5; este documento refleja las pruebas sobre `98dfdd6`.
3. **Alcance:** no se verificaron Groq con credencial real, pruebas de carga, pruebas de navegador automatizadas, todas las suites HTTP en este clon ni la restauración efectiva de un respaldo.
4. **Evidencia:** anexar capturas sanitizadas y, si se solicita, ejecutar una revisión adicional de endpoints protegidos sin modificar la base original.
5. **Seguridad:** no incluir `.env`, contraseñas, códigos temporales, JWT ni claves de pipeline en commits o archivos de entrega.

## 11. Conclusión

La instalación desde un clon nuevo del commit `98dfdd6` permitió construir e iniciar los servicios de PluriOne en un proyecto Docker aislado, con PostgreSQL independiente y correo local Mailpit. Se comprobó el registro y activación de un usuario nuevo, la recepción de correos, la recuperación de contraseña y el acceso al Dashboard. La incidencia de inicio de sesión inicial quedó documentada sin atribuir una causa no demostrada.

Al terminar se detuvo el clon y se restauró la plataforma original con sus contenedores y su volumen PostgreSQL conservados. Los resultados constituyen **evidencia técnica reproducible del MVP académico**, limitada a las operaciones realmente efectuadas y sin implicar certificación de seguridad o producción.


## 10. Validacion integral desde clon nuevo - 2026-10-29

Se realizo una instalacion desde un clon nuevo de GitHub,
correspondiente al commit 2872b92.

El clon se preparo en PluriOne_Validacion_Final_Corte6.

Se utilizo un proyecto Docker independiente llamado
plurione_validacion_final_c6.

Se generaron credenciales nuevas y un volumen PostgreSQL
independiente del proyecto principal.

### Puertos de la instalacion

| Servicio | Puerto |
| --- | --- |
| React | 5174 |
| FastAPI | 8001 |
| PostgreSQL | 5434 |
| Mailpit | 8026 |

Se utilizaron configuraciones locales para cambiar los
puertos y mantener ambas instalaciones separadas.

### Verificaciones

React, FastAPI y Mailpit respondieron HTTP 200.

PostgreSQL alcanzo el estado healthy.

La verificacion CORS devolvio HTTP 200 y autorizo
el origen http://127.0.0.1:5174.

### Registro y autenticacion

Se registro y verifico una cuenta nueva mediante React
y Mailpit en el clon independiente.

El primer inicio de sesion funciono sin recuperar
la contrasena.

La pestaña Network mostro POST /login/ con HTTP 200.

Se confirmo el acceso al Dashboard.

### Pipeline e ingesta

Se creo el pipeline pipeline-corte6-final.

La interfaz confirmo su creacion mediante HTTP 201.

Posteriormente, se envio una solicitud autenticada
a http://127.0.0.1:8001/metricas/externas/.

La metrica enviada fue latencia_ms con valor 9500.

La clave X-Pipeline-Key se introdujo de forma privada
y no se incorporo a la documentacion.

La API devolvio HTTP 201.

### Alerta critica

El Dashboard mostro una alerta critica correspondiente
al pipeline pipeline-corte6-final.

La alerta identifico la metrica latencia_ms
con el valor 9500.

El evento aparecio en el feed de alertas recientes
a las 10:59:08 del 29 de octubre de 2026.

### Conclusiones y limitaciones

La instalacion nueva permitio comprobar el recorrido
de registro, verificacion, primer login, creacion
de pipeline, ingesta HTTP 201 y alerta critica.

El proyecto principal y su base de datos se conservaron
sin modificaciones.

La causa exacta del HTTP 401 historico del Corte 5
continua sin demostrarse.

Esta prueba confirma el funcionamiento del flujo actual,
pero no constituye una certificacion de produccion.

No se publicaron contrasenas, codigos, JWT ni claves
de pipelines.


## 11. Investigacion complementaria del HTTP 401 - 2026-10-29

Se reviso el codigo historico de autenticacion del commit
98dfdd6 y se comparo con la correccion 3cbc283.

El registro historico almacenaba un hash bcrypt de la
contrasena original. La recuperacion generaba un nuevo
hash y el login verificaba la contrasena proporcionada
contra el hash almacenado.

Se identifico un mecanismo adicional que puede producir
HTTP 401 cuando una cuenta existente intenta registrarse
nuevamente con otra contrasena.

### Reproduccion controlada

Se utilizo el clon independiente del Corte 6, con
FastAPI en el puerto 8001 y PostgreSQL aislado.

Se genero una cuenta ficticia con correo aleatorio y
dos contrasenas distintas, sin publicar sus valores.

Resultados observados:

| Operacion | Resultado |
| --- | --- |
| Primer registro | HTTP 200 |
| Segundo registro con el mismo correo | HTTP 200 |
| Comparacion de respuestas de registro | Identicas |
| Login con la segunda contrasena | HTTP 401 |
| Login con la primera contrasena | HTTP 403 |

El segundo registro no reemplazo la contrasena original.

El HTTP 403 con la primera contrasena confirma que esta
fue reconocida, pero la cuenta permanecia sin verificar.

### Interpretacion

La respuesta generica del registro no confirma que se
haya creado otra cuenta ni que la contrasena se actualizara.

Este comportamiento puede explicar una secuencia donde
aparece HTTP 401 y posteriormente funciona el acceso
tras recuperar la contrasena.

Sin embargo, no se dispone de evidencia suficiente para
demostrar que hubo un segundo registro durante el
incidente historico del Corte 5.

Por tanto, se considera reproducido un mecanismo posible,
pero la causa exacta del HTTP 401 historico permanece
sin confirmacion forense.

No se modifico el codigo de autenticacion ni se publicaron
contrasenas, tokens, claves privadas o datos reales.
