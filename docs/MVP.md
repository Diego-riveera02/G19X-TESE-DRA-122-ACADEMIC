# Producto Mínimo Viable (MVP) — PluriOne
- Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
- Autor: Diego Rivera Aguilar
- Fecha: Octubre de 2026
- Versión documentada: Prototipo académico con J.A.R.V.I.S. 2.0
## 1. Alcance del MVP
El MVP de PluriOne busca validar localmente un ciclo básico de observabilidad: generación automática de métricas simuladas, almacenamiento de anomalías, visualización del estado de pipelines y obtención de diagnósticos orientativos con apoyo de inteligencia artificial.
Se trata de una implementación funcional de demostración. No realiza ingesta desde sistemas productivos, monitoreo real de AWS o intervención automática sobre infraestructura externa.
### 1.1. Autenticación y seguridad
Registro de usuarios, hash de contraseñas mediante bcrypt, verificación de cuentas con código de 6 dígitos enviado por SMTP, activación de cuenta e inicio de sesión con JWT. El formulario React de recuperación permite solicitar el código al correo registrado, introducirlo junto con una nueva contraseña y volver a iniciar sesión. El backend rechaza JWT de cuentas inexistentes o inactivas; restringe la lectura de anomalías al usuario autenticado. Las conexiones WebSocket también deben autenticarse antes de recibir eventos.
### 1.2. Motor de telemetría automática simulada
Proceso asíncrono en segundo plano (asyncio) integrado con FastAPI. Genera datos simulados de latencia (latencia_ms), integridad o calidad (datos_corruptos_%) y tasa de fallos (tasa_fallos_%) aproximadamente cada 5 segundos, sin interacción manual. Guarda los registros en PostgreSQL y transmite nuevas anomalías por WebSocket.
Las recomendaciones que acompañan la telemetría simulada se producen localmente mediante reglas o textos orientativos. No se invoca el modelo de Groq por cada evento generado.
### 1.3. Dashboard y alertas
Interfaz React con Recharts para visualizar métricas y estados (Normal, Alerta, Critico). Feed de anomalías recientes con valores, pipeline y fecha/hora enviada por el backend. Actualización de eventos sin recargar la página.
### 1.4. Asistente inteligente J.A.R.V.I.S. 2.0
Chat en español con Groq (modelo openai/gpt-oss-20b), historial limitado de conversación durante la sesión y function calling controlado por FastAPI.
La herramienta consultar_anomalias_usuario recupera información solo del usuario autenticado, permite filtrar por normal, alerta, critico o todos, contar registros coincidentes y presentar hasta 10 registros recientes por consulta. J.A.R.V.I.S. utiliza esa información para explicar métricas, proponer causas no verificadas y recomendar pasos de investigación seguros.
El frontend muestra respuestas con Markdown y tablas, desplazamiento independiente del chat y botón «↓ Último».
### 1.5. Historial, PDF y onboarding
Consulta de anomalías almacenadas, exportación a PDF de los registros cargados en la interfaz y guía interactiva inicial. La ocultación local del historial visible no debe documentarse como eliminación permanente de registros de la base de datos.
### 1.6. Infraestructura de desarrollo
Backend FastAPI, PostgreSQL, frontend React/Vite y Docker Compose para los servicios configurados en el entorno de pruebas. Credenciales, claves JWT y acceso a Groq/SMTP mediante variables de entorno.
## 2. Estado de desarrollo del MVP
- **Modelos y persistencia en PostgreSQL**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Registros de usuarios y anomalías; marcas de tiempo.

- **API y seguridad de acceso**
  - **Estado a octubre de 2026:** Implementado y comprobado localmente
  - **Evidencia o límite:** JWT, control de usuario y rechazo de cuentas inactivas; respuesta HTTP 401 sin token y con cuenta inactiva en las pruebas correspondientes. Requiere pruebas más amplias antes de producción.

- **Recuperación de contraseña desde React**
  - **Estado a octubre de 2026:** Implementado y probado manualmente
  - **Evidencia o límite:** El formulario solicita código SMTP, acepta el código para el restablecimiento y permite iniciar sesión con la nueva contraseña.

- **Telemetría automática**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Datos simulados generados periódicamente en FastAPI.

- **WebSocket por usuario**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Autenticación con JWT y recepción de eventos en la interfaz.

- **Dashboard y feed**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Gráficas, estados, alertas y horas de los registros.

- **Chat J.A.R.V.I.S. con Groq**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Preguntas generales y diagnósticos orientativos. Sujeto a límites y disponibilidad de Groq.

- **Herramienta de consulta SQL controlada**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Conteo y últimos registros por estado del usuario autenticado.

- **Memoria conversacional**
  - **Estado a octubre de 2026:** Implementado de forma limitada
  - **Evidencia o límite:** Hasta 10 mensajes anteriores enviados desde el frontend; no persiste entre sesiones.

- **Markdown y navegación del chat**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Tablas con desplazamiento y botón «↓ Último».

- **Historial, exportación PDF y onboarding**
  - **Estado a octubre de 2026:** Implementado
  - **Evidencia o límite:** Exportación de los datos cargados en la interfaz.

- **Docker Compose y compilación del frontend**
  - **Estado a octubre de 2026:** Probado localmente
  - **Evidencia o límite:** Servicios de API/BD iniciados y npm run build completado.

- **Ingesta desde pipelines empresariales reales**
  - **Estado a octubre de 2026:** Fuera del MVP
  - **Evidencia o límite:** No se conecta a fuentes productivas.

- **Consultas avanzadas por fecha o métrica en J.A.R.V.I.S.**
  - **Estado a octubre de 2026:** No implementado
  - **Evidencia o límite:** La herramienta actual filtra solo por estado.

- **Acciones correctivas automáticas en infraestructura**
  - **Estado a octubre de 2026:** Fuera del MVP
  - **Evidencia o límite:** El asistente recomienda; no opera sistemas externos.



## 3. Criterios de validación del MVP

**Cobertura automatizada actual:** las nueve pruebas verifican disponibilidad de FastAPI y React, rutas, rechazo de JWT ausentes o inválidos, CORS y conexión/esquema de PostgreSQL. Aún no incluyen pruebas específicas de expiración de códigos, cinco intentos fallidos, HTTP 429 o aislamiento entre usuarios.


### Validación adicional de la versión auditada

La versión actual incorpora reenvío de verificación, vencimiento de códigos, límite de cinco intentos, separación entre verificación y recuperación, y control de solicitudes de autenticación mediante PostgreSQL.

Se comprobó el arranque de una instalación limpia e independiente con Docker Compose, FastAPI, React y PostgreSQL. También se ejecutaron satisfactoriamente las nueve pruebas automatizadas disponibles en `backend/tests/test_integracion_http.py`.

Las pruebas no cubren de manera exhaustiva los flujos del navegador, SMTP, Groq, WebSocket, carga o seguridad de producción. La ingesta de datos empresariales reales continúa fuera del alcance del MVP.



1. Acceso controlado. El MVP contempla registro, verificación SMTP, inicio de sesión JWT y recuperación de contraseña. Los códigos vencen después de 10 minutos, admiten cinco intentos y se invalidan tras su uso. Se comprobó el rechazo HTTP 401 en las rutas protegidas evaluadas.
2. Automatización demostrable. El backend genera telemetría simulada aproximadamente cada 5 segundos sin intervención manual; la periodicidad es objetivo de la simulación, no garantía estricta de latencia.
3. Actualización de interfaz. Un usuario autenticado observa las nuevas anomalías por WebSocket sin recargar el dashboard.
4. Persistencia y trazabilidad. Las anomalías incluyen pipeline, métrica, valor, estado y fecha/hora registrada; el feed utiliza el tiempo proporcionado por el backend.
5. Diagnóstico contextualizado. J.A.R.V.I.S. puede recuperar anomalías del usuario por estado, indicar cantidades y elaborar hipótesis y recomendaciones sin afirmar que verificó logs o infraestructura externa.
6. Usabilidad. Los resultados extensos y las tablas se leen mediante desplazamiento dentro del chat; el historial visible puede exportarse a PDF.
7. Entorno reproducible. El proyecto dispone de instrucciones para levantar FastAPI/PostgreSQL y ejecutar/compilar React localmente.
Validaciones locales observadas en la iteración: compilación exitosa de Vite, arranque de los contenedores API y BD, recepción de telemetría, consultas conversacionales a registros y prueba del desplazamiento del chat. También se comprobó el envío de código SMTP desde la pantalla de React, su uso para restablecer la contraseña, el nuevo acceso al dashboard y respuestas HTTP 401 de rutas protegidas sin autorización. Estos resultados no equivalen a cobertura integral de pruebas automatizadas, auditoría de seguridad completa ni certificación de producción.
## 4. Lista de comprobación de entregables
Esta lista resume las funcionalidades incluidas en el MVP y las actividades que siguen pendientes.
- [x] Base de datos PostgreSQL y API FastAPI.
- [x] Simulación automática y eventos WebSocket por usuario.
- [x] Dashboard y registro de alertas con marca temporal.
- [x] J.A.R.V.I.S. 2.0 con Groq, herramienta autorizada y contexto reciente.
- [x] Presentación Markdown, historial, PDF y guía de bienvenida.
- [x] Ejecución local de servicios y compilación del frontend.
- [x] Recuperación de contraseña iniciada en React y finalizada con inicio de sesión nuevo.
- [x] Rechazo de acceso sin JWT y de cuentas inactivas en las rutas probadas.
- [ ] Integración real con sistemas productivos (fuera del MVP).
- [ ] Pruebas exhaustivas de seguridad y carga (pendientes).
## 5. Exclusiones y trabajo posterior
Quedan fuera del MVP o pendientes de una fase posterior: conectores reales de ingesta (AWS, bases corporativas y otros servicios), evaluación de causas raíz con evidencias externas, filtros complejos de consulta histórica, acciones de remediación automáticas, métricas de fiabilidad de producción, pruebas de carga y pruebas automatizadas de seguridad/aislamiento más exhaustivas.
Los correos SMTP se utilizan para verificación y recuperación de acceso. El simulador no envía un correo por cada anomalía. Los códigos tienen vencimiento temporal y un máximo de cinco intentos. El archivo `backend/app/schema_migrations.py` actualiza instalaciones anteriores sin eliminar los registros existentes.
## 6. Conclusión
El MVP demuestra la integración de FastAPI + PostgreSQL + WebSockets + React + Groq en un escenario controlado con datos simulados. J.A.R.V.I.S. 2.0 amplía la experiencia mediante conversación contextual y acceso restringido a registros del usuario. El resultado sirve para validación académica y demostración técnica, sin presentar la simulación como monitoreo de producción.
Documentos relacionados: [`../README.md`](../README.md) · [`PRD.md`](PRD.md) · [`../frontend/README.md`](../frontend/README.md).

## Actualizacion de la segunda auditoria - octubre de 2026

### Funcionalidades incorporadas al MVP

- Archivado logico del historial de anomalias por usuario.
- Restauracion del historial archivado.
- Consultas separadas de anomalias activas y archivadas.
- Acceso protegido por JWT a las operaciones del historial.
- Controles de React con confirmacion para archivar o restaurar.
- Migracion versionada de PostgreSQL para los campos de archivado.

El archivado es reversible: no constituye una eliminacion fisica de los
registros. Las vistas de historial utilizan consultas paginadas.

### Evidencia de pruebas

La segunda auditoria completo una compilacion de React/Vite y
17 pruebas automatizadas satisfactorias:

- Nueve pruebas de integracion de servicios y rutas principales.
- Ocho pruebas de autorizacion de rutas del historial, sin token
  y con token invalido.

Adicionalmente, el comportamiento de archivado y restauracion fue
verificado con una base de datos aislada, sin archivar registros
reales de PostgreSQL durante las pruebas.

### Limitaciones y pendientes

- La ingesta sigue siendo simulada, no empresarial real.
- No existe validacion exhaustiva de carga o de seguridad productiva.
- Las pruebas no cubren todos los flujos visuales del navegador.
- Las consultas iniciales pueden mostrar solo una pagina del historial.
- Falta una verificacion integral de SMTP y de servicios externos
  en un entorno de despliegue controlado.

Estos puntos deben conservarse como pendientes y no presentarse
como funcionalidades concluidas del MVP.
