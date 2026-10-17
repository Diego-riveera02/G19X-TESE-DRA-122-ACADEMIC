
# Frontend de PluriOne

## Descripción

El frontend de PluriOne es la interfaz web de la Plataforma de Observabilidad de Datos con Inteligencia Artificial.

Permite a los usuarios autenticados visualizar métricas simuladas de pipelines de datos, consultar anomalías, revisar su historial y recibir recomendaciones técnicas mediante el asistente J.A.R.V.I.S.

## Tecnologías utilizadas

- React.js: desarrollo de la interfaz.
- Vite: entorno de desarrollo y compilación.
- React Router: navegación entre las pantallas.
- Axios: comunicación con la API de FastAPI.
- Recharts: visualización de métricas mediante gráficas.
- WebSockets: recepción de anomalías en tiempo real.
- jsPDF y jspdf-autotable: generación de reportes PDF.

## Funcionalidades principales

- Registro, verificación e inicio de sesión de usuarios.
- Dashboard con métricas de latencia, calidad de datos y fallos.
- Actualización de gráficas y alertas mediante WebSockets.
- Consulta del historial de anomalías.
- Exportación de reportes en formato PDF.
- Asistente J.A.R.V.I.S. para consultas y recomendaciones técnicas.
- Guía interactiva de bienvenida.

## Requisitos previos

- Node.js y npm.
- Backend de PluriOne configurado y en ejecución.
- Base de datos PostgreSQL disponible para el backend.

## Instalación

Desde la carpeta `frontend`, ejecutar:

```bash
npm install
```

## Ejecución en desarrollo

Iniciar el servidor de Vite:

```bash
npm run dev
```

Abrir en el navegador:

http://127.0.0.1:5173

## Compilación

Para generar la versión de producción:

```bash
npm run build
```

## Comunicación con el backend

El frontend se comunica con la API desarrollada en FastAPI.

En el entorno local utilizado durante las pruebas, el backend está disponible en:

http://127.0.0.1:8000

La comunicación en tiempo real se realiza mediante WebSockets autenticados con JWT.

Cada conexión recibe los eventos destinados al usuario correspondiente.

## Origen de los datos

Actualmente, PluriOne utiliza un simulador automático implementado en el backend.

Este simulador genera métricas de prueba y las almacena en PostgreSQL.

El frontend muestra esa información y recibe nuevas anomalías sin necesidad de ejecutar manualmente la generación de datos.

En esta etapa, no existe una conexión directa con pipelines empresariales reales.

## Documentación adicional

Consultar el archivo README.md de la raíz del repositorio y los documentos docs/PRD.md y docs/MVP.md.

## Proyecto académico

Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne).