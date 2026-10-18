# Frontend de PluriOne

## 1. Descripción
El frontend es la interfaz web del prototipo académico PluriOne: Plataforma de Observabilidad de Datos con Inteligencia Artificial. Permite a usuarios autenticados consultar métricas simuladas de pipelines, observar alertas, revisar registros y conversar con el asistente J.A.R.V.I.S. 2.0.
No existe en esta etapa una conexión directa del frontend con pipelines empresariales productivos. Los datos provienen del backend de FastAPI y se almacenan en PostgreSQL.

## 2. Tecnologías utilizadas
- React y Vite: componentes, entorno de desarrollo y compilación.
- React Router: navegación entre acceso, registro, verificación, recuperación y dashboard.
- Axios: solicitudes a la API de FastAPI.
- Recharts: gráficas de latencia, calidad de datos y fallos.
- WebSocket: recepción de anomalías en tiempo real después de autenticar la conexión mediante JWT.
- react-markdown y remark-gfm: visualización de respuestas del asistente con títulos, listas, negritas y tablas.
- jsPDF y jspdf-autotable: exportación a PDF de la bitácora cargada en la interfaz.

## 3. Funcionalidades implementadas

### Reenvío de verificación

- Desde la pantalla de verificación, el usuario puede solicitar otro código si no recibió el anterior.
- React utiliza `POST /reenviar-verificacion/` del backend.
- El reenvío y la validación están sujetos a los controles de seguridad del servidor.
- Registro de usuarios, verificación de cuenta mediante código e inicio de sesión. La pantalla Recuperar Acceso incluye el botón Enviar código de recuperación, que solicita un código por SMTP al backend; después permite validar ese código y establecer la nueva contraseña.
- Dashboard con tres visualizaciones de métricas y distintivos de estado Normal, Alerta y Critico.
- Feed de alertas recientes con hora del registro enviada por el backend, en vez de usar la hora actual del navegador.
- Actualización de anomalías mediante WebSocket autenticado y filtrado por usuario desde el servidor; controles para evitar duplicados en la interfaz.
- Historial de anomalías y generación de PDF de los registros disponibles en la vista.
- Chat con J.A.R.V.I.S., integrado con el endpoint autenticado /chat/.
- Envío de hasta 10 mensajes previos recientes para conservar el contexto conversacional durante la sesión del frontend.
- Interpretación de respuestas Markdown mediante react-markdown y remark-gfm.
- Tablas extensas con desplazamiento horizontal dentro del chat, desplazamiento vertical de la conversación y botón «↓ Último».
- Guía de bienvenida interactiva (onboarding).
La opción Vaciar Tabla del historial visible no debe confundirse con la eliminación definitiva de registros en PostgreSQL: el frontend puede ocultarlos localmente.

## 4. Requisitos previos
- Node.js y npm compatibles con la versión de Vite definida en package.json.
- Backend FastAPI ejecutándose en el entorno local configurado.
- PostgreSQL disponible para el backend; el navegador no se conecta directamente a la base de datos.
- Sesión de usuario válida para consultar información protegida.

## 5. Instalación y ejecución

### Ejecución del proyecto con Docker Compose

Desde la raíz del repositorio, configurar los archivos `.env` a partir de sus ejemplos y ejecutar:

```powershell
docker compose up -d --build
```

En la configuración local probada, React utiliza el puerto 5173 y FastAPI el puerto 8000.

No utilizar `docker compose down -v` cuando sea necesario conservar los datos del volumen PostgreSQL.

Desde la carpeta frontend/:

```powershell
npm install
npm run dev
```

En el entorno local probado, abrir:
http://127.0.0.1:5173/app
Desde la raíz del repositorio, se puede hacer lo mismo sin cambiar de carpeta:

```powershell
npm --prefix ./frontend install
npm --prefix ./frontend run dev
```

Compilación de producción:

```powershell
npm run build
```

O, desde la raíz:

```powershell
npm --prefix ./frontend run build
```

Si aparece un aviso de tamaño de chunks superior a 500 kB, se trata de una advertencia de optimización y no necesariamente de un error de compilación.

## 6. Comunicación con el backend
En la configuración local utilizada durante el desarrollo:
- API HTTP: http://127.0.0.1:8000
- WebSocket: ws://127.0.0.1:8000/ws/anomalias
- Interfaz: http://127.0.0.1:5173
El frontend envía el token JWT en las solicitudes autenticadas a FastAPI. Al abrir WebSocket transmite un mensaje de autenticación y recibe eventos de anomalías destinados al usuario correspondiente. La seguridad y separación entre cuentas deben aplicarse en el backend, no depender exclusivamente de filtros de React. En las rutas protegidas comprobadas, FastAPI también rechaza las cuentas inactivas aunque presenten un JWT válido.
La vista del feed utiliza el campo timestamp de cada anomalía. Para los eventos nuevos, el backend envía una fecha UTC serializada, que el navegador presenta en formato de hora local.
Ejemplo del primer mensaje de autenticación del WebSocket, sin incluir un token real:
{
  "type": "auth",
  "token": "TOKEN_JWT_DE_EJEMPLO"
}
El backend valida el token y solamente después permite recibir los eventos del usuario autenticado.

### Interfaces de comunicación utilizadas
- GET /anomalias/	Recuperar anomalías del usuario.	JWT en la solicitud HTTP.
- POST /chat/	Enviar preguntas al asistente.	JWT; herramientas restringidas en FastAPI.
- POST /solicitar-recuperacion/	Solicitar un código SMTP para el correo registrado desde el formulario de recuperación.	Solicitud pública de recuperación; no requiere JWT.
- POST /recuperar-password/	Enviar correo, código recibido y nueva contraseña para restablecer el acceso.	Requiere la coincidencia del código guardado para esa cuenta.
- ws://127.0.0.1:8000/ws/anomalias	Recibir anomalías nuevas.	Mensaje de autenticación JWT.


### Recuperación de acceso desde la interfaz
1. Desde Login, elegir ¿Olvidaste tu contraseña? para abrir /recuperar.
2. Escribir el correo registrado y pulsar Enviar código de recuperación. El botón se deshabilita durante la solicitud para evitar clics simultáneos.
3. Consultar el correo más reciente, introducir el código de seis dígitos y la nueva contraseña y pulsar Actualizar Contraseña.
4. Volver al inicio de sesión y autenticarse con la contraseña actualizada.
En la prueba manual local de octubre de 2026 se recibió el correo SMTP, se actualizó la contraseña y se pudo acceder nuevamente al dashboard.

La versión auditada incorpora códigos con vencimiento temporal, un máximo de cinco intentos y propósitos separados para verificación y recuperación. El backend también limita solicitudes de autenticación mediante PostgreSQL.

## 7. J.A.R.V.I.S. 2.0: capacidades y límites
El chat permite preguntas generales sobre observabilidad, seguimiento de la conversación reciente y consultas acerca de las anomalías del usuario. Cuando necesita registros concretos, el backend puede invocar la herramienta autorizada consultar_anomalias_usuario, que filtra por estado (normal, alerta, critico, todos) y devuelve el total y hasta 10 registros recientes.
No se han implementado en esa herramienta filtros arbitrarios por fechas, severidad, palabras clave o métricas. Las explicaciones sobre posibles causas no sustituyen una investigación técnica de sistemas reales.
Las respuestas se muestran con formato Markdown y tablas desplazables dentro del panel. El botón «↓ Último» lleva al mensaje más reciente sin desplazar toda la página. La memoria conversacional es limitada y no constituye un historial persistente entre sesiones.

## 8. Origen de los datos
FastAPI ejecuta un simulador automático de telemetría que genera registros de prueba aproximadamente cada 5 segundos y los guarda en PostgreSQL. WebSocket distribuye esos eventos a las sesiones autorizadas. Las recomendaciones automáticas de la simulación se generan localmente; el uso de Groq corresponde al chat de J.A.R.V.I.S.
Advertencia: ninguna métrica presentada permite concluir, por sí sola, que hay un incidente real en infraestructura empresarial.

## 9. Comprobaciones y documentación

### Pruebas automatizadas de integracion

PluriOne incluye la suite permanente
`backend/tests/test_integracion_http.py`.

Con FastAPI, React y PostgreSQL iniciados mediante Docker Compose,
ejecutar desde la raiz del repositorio:

```powershell
python -m unittest discover -s backend/tests -p "test_*.py" -v
```

La suite contiene nueve pruebas automatizadas que verifican
la disponibilidad de FastAPI y React, las rutas principales,
el rechazo de JWT ausentes o invalidos, la configuracion
CORS y la conexion con PostgreSQL.

En la auditoria de octubre de 2026, las nueve pruebas
finalizaron satisfactoriamente.

Estas comprobaciones no sustituyen pruebas exhaustivas
de interfaz, SMTP, Groq, WebSocket, carga o seguridad
de produccion.


### Pruebas automatizadas disponibles

Con los servicios locales iniciados, ejecutar desde la raíz del repositorio:

```powershell
python -m unittest discover -s backend/tests -p "test_*.py" -v
```

La suite contiene nueve pruebas de integración que comprobaron FastAPI, React, rutas registradas, rechazo de JWT ausentes o inválidos, CORS y PostgreSQL. Las nueve finalizaron correctamente en la revisión de octubre de 2026.

Para revisar el frontend también están disponibles `npm run build`, `npm run lint` y `npm audit`. La existencia de estos comandos no implica que todas las verificaciones se hayan ejecutado en esta misma revisión.

Para verificar los cambios del frontend:

```powershell
npm run build
npm audit
```

La auditoría de seguridad realizada en octubre de 2026 terminó con 0 vulnerabilidades reportadas en el entorno de pruebas, después de actualizar una dependencia afectada. Esto no garantiza ausencia permanente de vulnerabilidades.
Documentos relacionados:
- [`../README.md`](../README.md) — descripción general e instrucciones del proyecto.
- [`../docs/MVP.md`](../docs/MVP.md) — alcance del prototipo.
- [`../docs/PRD.md`](../docs/PRD.md) — requisitos del producto.

## 10. Lista de verificación del frontend
- [x] Navegación y pantallas de autenticación.
- [x] Gráficas, feed de alertas y WebSocket autenticado.
- [x] Chat con Markdown, tablas desplazables y botón «↓ Último».
- [x] Compilación local y auditoría de paquetes realizadas en octubre de 2026.
- [ ] Pruebas automatizadas de interfaz y accesibilidad exhaustivas (pendientes).
Proyecto académico: PluriOne. Documentación revisada en octubre de 2026.
