Producto Mínimo Viable (MVP) — PluriOne
- Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
- Autor: Diego Rivera Aguilar
- Fecha: Octubre de 2026
- Versión documentada: Prototipo académico con J.A.R.V.I.S. 2.0
1. Alcance del MVP
El MVP de PluriOne busca validar localmente un ciclo básico de observabilidad: generación automática de métricas simuladas, almacenamiento de anomalías, visualización del estado de pipelines y obtención de diagnósticos orientativos con apoyo de inteligencia artificial.
Se trata de una implementación funcional de demostración. No realiza ingesta desde sistemas productivos, monitoreo real de AWS o intervención automática sobre infraestructura externa.
1.1. Autenticación y seguridad
Registro de usuarios, hash de contraseñas mediante bcrypt, verificación de cuentas con código de 6 dígitos enviado por SMTP, activación de cuenta, inicio de sesión con JWT y recuperación de contraseña con código. El backend restringe la lectura de anomalías al usuario autenticado; las conexiones WebSocket deben autenticarse antes de recibir eventos.
1.2. Motor de telemetría automática simulada
Proceso asíncrono en segundo plano (asyncio) integrado con FastAPI. Genera datos simulados de latencia (latencia_ms), integridad o calidad (datos_corruptos_%) y tasa de fallos (tasa_fallos_%) aproximadamente cada 5 segundos, sin interacción manual. Guarda los registros en PostgreSQL y transmite nuevas anomalías por WebSocket.
Las recomendaciones que acompañan la telemetría simulada se producen localmente mediante reglas o textos orientativos. No se invoca el modelo de Groq por cada evento generado.
1.3. Dashboard y alertas
Interfaz React con Recharts para visualizar métricas y estados (Normal, Alerta, Critico). Feed de anomalías recientes con valores, pipeline y fecha/hora enviada por el backend. Actualización de eventos sin recargar la página.
1.4. Asistente inteligente J.A.R.V.I.S. 2.0
Chat en español con Groq (modelo openai/gpt-oss-20b), historial limitado de conversación durante la sesión y function calling controlado por FastAPI.
La herramienta consultar_anomalias_usuario recupera información solo del usuario autenticado, permite filtrar por normal, alerta, critico o todos, contar registros coincidentes y presentar hasta 10 registros recientes por consulta. J.A.R.V.I.S. utiliza esa información para explicar métricas, proponer causas no verificadas y recomendar pasos de investigación seguros.
El frontend muestra respuestas con Markdown y tablas, desplazamiento independiente del chat y botón «↓ Último».
1.5. Historial, PDF y onboarding
Consulta de anomalías almacenadas, exportación a PDF de los registros cargados en la interfaz y guía interactiva inicial. La ocultación local del historial visible no debe documentarse como eliminación permanente de registros de la base de datos.
1.6. Infraestructura de desarrollo
Backend FastAPI, PostgreSQL, frontend React/Vite y Docker Compose para los servicios configurados en el entorno de pruebas. Credenciales, claves JWT y acceso a Groq/SMTP mediante variables de entorno.
2. Estado de desarrollo del MVP
Componente	Estado a octubre de 2026	Evidencia o límite
Modelos y persistencia en PostgreSQL	Implementado	Registros de usuarios y anomalías; marcas de tiempo.
API y seguridad de acceso	Implementado	Rutas de cuenta, JWT y control de usuario. Requiere pruebas de seguridad exhaustivas antes de producción.
Telemetría automática	Implementado	Datos simulados generados periódicamente en FastAPI.
WebSocket por usuario	Implementado	Autenticación con JWT y recepción de eventos en la interfaz.
Dashboard y feed	Implementado	Gráficas, estados, alertas y horas de los registros.
Chat J.A.R.V.I.S. con Groq	Implementado	Preguntas generales y diagnósticos orientativos. Sujeto a límites y disponibilidad de Groq.
Herramienta de consulta SQL controlada	Implementado	Conteo y últimos registros por estado del usuario autenticado.
Memoria conversacional	Implementado de forma limitada	Hasta 10 mensajes anteriores enviados desde el frontend; no persiste entre sesiones.
Markdown y navegación del chat	Implementado	Tablas con desplazamiento y botón «↓ Último».
Historial, exportación PDF y onboarding	Implementado	Exportación de los datos cargados en la interfaz.
Docker Compose y compilación del frontend	Probado localmente	Servicios de API/BD iniciados y npm run build completado.
Ingesta desde pipelines empresariales reales	Fuera del MVP	No se conecta a fuentes productivas.
Consultas avanzadas por fecha o métrica en J.A.R.V.I.S.	No implementado	La herramienta actual filtra solo por estado.
Acciones correctivas automáticas en infraestructura	Fuera del MVP	El asistente recomienda; no opera sistemas externos.


3. Criterios de validación del MVP
1. Acceso controlado. El flujo de usuario contempla registro, verificación SMTP, inicio de sesión con JWT y recuperación de contraseña. Verificar por separado casos válidos, expiración y accesos denegados.
2. Automatización demostrable. El backend genera telemetría simulada aproximadamente cada 5 segundos sin intervención manual; la periodicidad es objetivo de la simulación, no garantía estricta de latencia.
3. Actualización de interfaz. Un usuario autenticado observa las nuevas anomalías por WebSocket sin recargar el dashboard.
4. Persistencia y trazabilidad. Las anomalías incluyen pipeline, métrica, valor, estado y fecha/hora registrada; el feed utiliza el tiempo proporcionado por el backend.
5. Diagnóstico contextualizado. J.A.R.V.I.S. puede recuperar anomalías del usuario por estado, indicar cantidades y elaborar hipótesis y recomendaciones sin afirmar que verificó logs o infraestructura externa.
6. Usabilidad. Los resultados extensos y las tablas se leen mediante desplazamiento dentro del chat; el historial visible puede exportarse a PDF.
7. Entorno reproducible. El proyecto dispone de instrucciones para levantar FastAPI/PostgreSQL y ejecutar/compilar React localmente.
Validaciones locales observadas en la iteración: compilación exitosa de Vite, arranque de los contenedores API y BD, recepción de telemetría, consultas conversacionales a registros y prueba del desplazamiento del chat. Estos resultados no equivalen a cobertura integral de pruebas automatizadas, auditoría de seguridad completa ni certificación de producción.
4. Lista de comprobación de entregables
Estas casillas describen el alcance documentado, no sustituyen las pruebas del profesor.
- [x] Base de datos PostgreSQL y API FastAPI.
- [x] Simulación automática y eventos WebSocket por usuario.
- [x] Dashboard y registro de alertas con marca temporal.
- [x] J.A.R.V.I.S. 2.0 con Groq, herramienta autorizada y contexto reciente.
- [x] Presentación Markdown, historial, PDF y guía de bienvenida.
- [x] Ejecución local de servicios y compilación del frontend.
- [ ] Integración real con sistemas productivos (fuera del MVP).
- [ ] Pruebas exhaustivas de seguridad y carga (pendientes).
5. Exclusiones y trabajo posterior
Quedan fuera del MVP o pendientes de una fase posterior: conectores reales de ingesta (AWS, bases corporativas y otros servicios), evaluación de causas raíz con evidencias externas, filtros complejos de consulta histórica, acciones de remediación automáticas, métricas de fiabilidad de producción, pruebas de carga y pruebas automatizadas de seguridad/aislamiento más exhaustivas.
Los correos SMTP se reservan al flujo de identidad y recuperación de acceso; el simulador no envía un correo por cada alerta para evitar tráfico masivo.
6. Conclusión
El MVP demuestra la integración de FastAPI + PostgreSQL + WebSockets + React + Groq en un escenario controlado con datos simulados. J.A.R.V.I.S. 2.0 amplía la experiencia mediante conversación contextual y acceso restringido a registros del usuario. El resultado sirve para validación académica y demostración técnica, sin presentar la simulación como monitoreo de producción.
Documentos relacionados: [`../README.md`](../README.md) · [`PRD.md`](PRD.md) · [`../frontend/README.md`](../frontend/README.md).