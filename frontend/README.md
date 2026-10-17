Frontend de PluriOne
1. Descripción
El frontend es la interfaz web del prototipo académico PluriOne: Plataforma de Observabilidad de Datos con Inteligencia Artificial. Permite a usuarios autenticados consultar métricas simuladas de pipelines, observar alertas, revisar registros y conversar con el asistente J.A.R.V.I.S. 2.0.
No existe en esta etapa una conexión directa del frontend con pipelines empresariales productivos. Los datos provienen del backend de FastAPI y se almacenan en PostgreSQL.
2. Tecnologías utilizadas
- React y Vite: componentes, entorno de desarrollo y compilación.
- React Router: navegación entre acceso, registro, verificación, recuperación y dashboard.
- Axios: solicitudes a la API de FastAPI.
- Recharts: gráficas de latencia, calidad de datos y fallos.
- WebSocket: recepción de anomalías en tiempo real después de autenticar la conexión mediante JWT.
- react-markdown y remark-gfm: visualización de respuestas del asistente con títulos, listas, negritas y tablas.
- jsPDF y jspdf-autotable: exportación a PDF de la bitácora cargada en la interfaz.
3. Funcionalidades implementadas
- Registro de usuarios, verificación de cuenta mediante código, inicio de sesión y recuperación de contraseña, en coordinación con el backend.
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
4. Requisitos previos
- Node.js y npm compatibles con la versión de Vite definida en package.json.
- Backend FastAPI ejecutándose en el entorno local configurado.
- PostgreSQL disponible para el backend; el navegador no se conecta directamente a la base de datos.
- Sesión de usuario válida para consultar información protegida.
5. Instalación y ejecución
Desde la carpeta frontend/:
npm install
npm run dev
En el entorno local probado, abrir:
http://127.0.0.1:5173/app
Desde la raíz del repositorio, se puede hacer lo mismo sin cambiar de carpeta:
npm --prefix ./frontend install
npm --prefix ./frontend run dev
Compilación de producción:
npm run build
O, desde la raíz:
npm --prefix ./frontend run build
Si aparece un aviso de tamaño de chunks superior a 500 kB, se trata de una advertencia de optimización y no necesariamente de un error de compilación.
6. Comunicación con el backend
En la configuración local utilizada durante el desarrollo:
- API HTTP: http://127.0.0.1:8000
- WebSocket: ws://127.0.0.1:8000/ws/anomalias
- Interfaz: http://127.0.0.1:5173
El frontend envía el token JWT en las solicitudes autenticadas a FastAPI. Al abrir WebSocket transmite un mensaje de autenticación y recibe eventos de anomalías destinados al usuario correspondiente. La seguridad y separación entre cuentas deben aplicarse en el backend, no depender exclusivamente de filtros de React.
La vista del feed utiliza el campo timestamp de cada anomalía. Para los eventos nuevos, el backend envía una fecha UTC serializada, que el navegador presenta en formato de hora local.
Ejemplo del primer mensaje de autenticación del WebSocket, sin incluir un token real:
{
  "type": "auth",
  "token": "TOKEN_JWT_DE_EJEMPLO"
}
El backend valida el token y solamente después permite recibir los eventos del usuario autenticado.
Interfaces de comunicación utilizadas
Interfaz	Función	Protección
GET /anomalias/	Recuperar anomalías del usuario.	JWT en la solicitud HTTP.
POST /chat/	Enviar preguntas al asistente.	JWT; herramientas restringidas en FastAPI.
ws://127.0.0.1:8000/ws/anomalias	Recibir anomalías nuevas.	Mensaje de autenticación JWT.


7. J.A.R.V.I.S. 2.0: capacidades y límites
El chat permite preguntas generales sobre observabilidad, seguimiento de la conversación reciente y consultas acerca de las anomalías del usuario. Cuando necesita registros concretos, el backend puede invocar la herramienta autorizada consultar_anomalias_usuario, que filtra por estado (normal, alerta, critico, todos) y devuelve el total y hasta 10 registros recientes.
No se han implementado en esa herramienta filtros arbitrarios por fechas, severidad, palabras clave o métricas. Las explicaciones sobre posibles causas no sustituyen una investigación técnica de sistemas reales.
Las respuestas se muestran con formato Markdown y tablas desplazables dentro del panel. El botón «↓ Último» lleva al mensaje más reciente sin desplazar toda la página. La memoria conversacional es limitada y no constituye un historial persistente entre sesiones.
8. Origen de los datos
FastAPI ejecuta un simulador automático de telemetría que genera registros de prueba aproximadamente cada 5 segundos y los guarda en PostgreSQL. WebSocket distribuye esos eventos a las sesiones autorizadas. Las recomendaciones automáticas de la simulación se generan localmente; el uso de Groq corresponde al chat de J.A.R.V.I.S.
Advertencia: ninguna métrica presentada permite concluir, por sí sola, que hay un incidente real en infraestructura empresarial.

9. Comprobaciones y documentación
Para verificar los cambios del frontend:
npm run build
npm audit
La auditoría de seguridad realizada en octubre de 2026 terminó con 0 vulnerabilidades reportadas en el entorno de pruebas, después de actualizar una dependencia afectada. Esto no garantiza ausencia permanente de vulnerabilidades.
Documentos relacionados:
- [`../README.md`](../README.md) — descripción general e instrucciones del proyecto.
- [`../docs/MVP.md`](../docs/MVP.md) — alcance del prototipo.
- [`../docs/PRD.md`](../docs/PRD.md) — requisitos del producto.
10. Lista de verificación del frontend
- [x] Navegación y pantallas de autenticación.
- [x] Gráficas, feed de alertas y WebSocket autenticado.
- [x] Chat con Markdown, tablas desplazables y botón «↓ Último».
- [x] Compilación local y auditoría de paquetes realizadas en octubre de 2026.
- [ ] Pruebas automatizadas de interfaz y accesibilidad exhaustivas (pendientes).
Proyecto académico: PluriOne. Documentación revisada en octubre de 2026.