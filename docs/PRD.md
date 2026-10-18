# Documento de Requisitos del Producto (PRD) — PluriOne
- Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
- Empresa: PluriOne S.A. de C.V.
- Autor: Diego Rivera Aguilar
- Fecha: Octubre de 2026
- Versión documentada: Prototipo académico con J.A.R.V.I.S. 2.0
## 1. Propósito, problemática y visión general
Problemática
El seguimiento de pipelines de datos puede resultar reactivo: los fallos, la latencia y los datos inconsistentes dificultan detectar problemas oportunamente y orientar la investigación técnica. Una vista centralizada de métricas y anomalías favorece el análisis operativo.
Propósito y visión
Desarrollar una plataforma que centralice métricas y alertas de prueba, permita observar su evolución y ofrezca diagnósticos orientativos mediante un asistente de IA. La versión actual está diseñada para demostración académica con telemetría simulada; la conexión a infraestructuras productivas corresponde a una posible evolución futura.
## 2. Público objetivo y objetivos del proyecto
Público objetivo
- Ingenieros de Datos y DataOps: seguimiento de estados y exploración de incidentes representados por métricas.
- Líderes técnicos y responsables de observabilidad: consulta de tableros, tendencias y bitácoras.
- Administradores de la plataforma: supervisión de los flujos de registro, autenticación y acceso de usuarios.
Objetivos específicos
1. Implementar registro, verificación por código SMTP, autenticación JWT, almacenamiento de contraseñas mediante hash y recuperación de acceso iniciada desde el formulario React con envío de código al correo registrado.
2. Generar automáticamente métricas simuladas en el backend y persistir las anomalías en PostgreSQL.
3. Mostrar gráficas y alertas con actualización en tiempo real mediante WebSocket autenticado por usuario.
4. Proporcionar un asistente conversacional que consulte datos del usuario mediante herramientas backend autorizadas y distinga hechos de hipótesis.
5. Consultar registros y generar reportes PDF a partir de los datos cargados en la interfaz.
6. Mantener instrucciones reproducibles de instalación, configuración y ejecución local.
## 3. Alcance del proyecto
Dentro del alcance del prototipo actual
- Alta y validación de cuentas, autenticación con bloqueo de cuentas inactivas y recuperación de acceso solicitando el código SMTP desde React.
- Simulador asíncrono de telemetría con registros de latencia, calidad e incidencias de fallos cada ~5 segundos.
- Persistencia y consulta de anomalías en PostgreSQL con marca de tiempo.
- Distribución en tiempo real por WebSocket con autenticación JWT y segmentación por usuario.
- Dashboard React/Vite con Recharts, estados y feed de alertas.
- J.A.R.V.I.S. 2.0 con Groq, conversación contextual limitada y herramienta para consultar anomalías por estado del usuario autenticado.
- Explicaciones y recomendaciones técnicas orientativas, no verificaciones independientes de causas raíz.
- Respuestas Markdown, tablas desplazables, botón «↓ Último», onboarding y exportación PDF.
- Entorno local de desarrollo con Docker Compose para API/base de datos y Vite para el frontend.
Fuera del alcance de esta versión
- Integración automática con pipelines de producción, AWS S3 real u otras infraestructuras externas.
- Cambios, escrituras, restauraciones o correcciones automáticas sobre servicios productivos.
- Confirmación de causas raíz mediante inspección real de logs, red, CPU o infraestructura.
- Filtros conversacionales avanzados por rango de fechas, severidad, palabra clave o métrica; la herramienta actual permite filtrar por estado.
- Memoria de chat permanente o compartida entre dispositivos/sesiones.
- Garantías de disponibilidad, escalabilidad o preparación para despliegue empresarial.
- Correos masivos por cada evento de telemetría: SMTP se utiliza para identidad y recuperación.
## 4. Requisitos funcionales e historias de usuario
- **RF-01**
  - **Requisito / historia de usuario:** Como usuario nuevo, quiero registrarme y verificar mi cuenta mediante un código enviado por correo.
  - **Estado de la versión documentada:** Implementado.

- **RF-02**
  - **Requisito / historia de usuario:** Como usuario, quiero iniciar sesión con JWT y recuperar mi contraseña solicitando un código por correo desde React, introduciéndolo y estableciendo una contraseña nueva.
  - **Estado de la versión documentada:** Implementado y probado manualmente; permite volver a iniciar sesión.

- **RF-02A**
  - **Requisito / historia de usuario:** Como usuario cuya cuenta fue desactivada, no debo conservar acceso a rutas protegidas aunque tenga un JWT anterior.
  - **Estado de la versión documentada:** Implementado; se comprobó respuesta HTTP 401 con cuenta inactiva.

- **RF-03**
  - **Requisito / historia de usuario:** Como operador, quiero recibir automáticamente métricas simuladas y consultarlas sin disparar eventos manualmente.
  - **Estado de la versión documentada:** Implementado.

- **RF-04**
  - **Requisito / historia de usuario:** Como operador, quiero visualizar latencia, datos corruptos y fallos en el dashboard.
  - **Estado de la versión documentada:** Implementado.

- **RF-05**
  - **Requisito / historia de usuario:** Como usuario autenticado, quiero recibir por WebSocket únicamente los eventos correspondientes a mi cuenta.
  - **Estado de la versión documentada:** Implementado; requiere pruebas sistemáticas de aislamiento como parte de la validación.

- **RF-06**
  - **Requisito / historia de usuario:** Como analista, quiero conocer el estado, valor y hora de cada anomalía reciente.
  - **Estado de la versión documentada:** Implementado.

- **RF-07**
  - **Requisito / historia de usuario:** Como analista, quiero preguntarle a J.A.R.V.I.S. por anomalías críticas o normales, y recibir cantidades y registros recientes de mi cuenta.
  - **Estado de la versión documentada:** Implementado mediante herramienta con filtro por estado.

- **RF-08**
  - **Requisito / historia de usuario:** Como analista, quiero recibir posibles causas y recomendaciones de investigación sin presentar hipótesis como hechos comprobados.
  - **Estado de la versión documentada:** Implementado como asistencia orientativa.

- **RF-09**
  - **Requisito / historia de usuario:** Como usuario, quiero mantener el contexto de mis últimas preguntas en el chat.
  - **Estado de la versión documentada:** Implementado de forma limitada a los mensajes recientes de la sesión.

- **RF-10**
  - **Requisito / historia de usuario:** Como usuario, quiero leer las respuestas con títulos, listas y tablas navegables sin deformar el dashboard.
  - **Estado de la versión documentada:** Implementado con Markdown y desplazamiento interno.

- **RF-11**
  - **Requisito / historia de usuario:** Como usuario, quiero consultar mi historial disponible y exportarlo a PDF.
  - **Estado de la versión documentada:** Implementado para los registros cargados en la interfaz.

- **RF-12**
  - **Requisito / historia de usuario:** Como usuario nuevo, quiero una guía interactiva de bienvenida.
  - **Estado de la versión documentada:** Implementado.



### Requisitos no funcionales
- RNF-01 — Seguridad: contraseñas mediante hash, JWT, verificación de cuentas, credenciales en variables de entorno y control de acceso en los endpoints y WebSockets. El backend debe rechazar JWT de cuentas inexistentes o inactivas. Ninguna clave secreta debe almacenarse en el repositorio.
- RNF-02 — Aislamiento: las consultas de anomalías y la transmisión de eventos deben limitarse al usuario autenticado.
- RNF-03 — Tiempo real: la simulación busca generar eventos aproximadamente cada 5 segundos y propagarlos sin recarga manual. No se promete una latencia estricta garantizada.
- RNF-04 — Persistencia: almacenar usuarios y anomalías con marca de tiempo en PostgreSQL.
- RNF-05 — Usabilidad: conservar legibilidad de gráficas, estados, tablas extensas y chat; el desplazamiento de una tabla no debe ensanchar todo el dashboard.
- RNF-06 — Trazabilidad de IA: indicar que los datos son simulados, distinguir valores de base de datos de hipótesis y no ofrecer capacidades inexistentes.
- RNF-07 — Operación segura: no ejecutar modificaciones sobre infraestructura externa a partir de una recomendación del asistente.
- RNF-08 — Configurabilidad: documentar dependencias, variables de entorno e instrucciones de ejecución y compilación local.
## 5. Arquitectura del sistema y tecnologías
- **Generación de datos:** Simulador asíncrono en Python/FastAPI.

- **Backend:** FastAPI, rutas HTTP y WebSocket; lógica de autenticación y autorización.

- **Persistencia:** PostgreSQL mediante modelos SQLAlchemy.

- **Inteligencia artificial:** Groq, modelo openai/gpt-oss-20b, función autorizada consultar_anomalias_usuario.

- **Interfaz web:** React, Vite, React Router, Axios, Recharts.

- **Presentación de diagnósticos:** react-markdown, remark-gfm; tablas y chat con desplazamiento controlado.

- **Reportes:** jsPDF y jspdf-autotable.

- **Mensajería SMTP:** Envío de códigos de registro y recuperación de acceso solicitados desde el formulario de React.

- **Entorno local:** Docker Compose y herramientas locales de desarrollo frontend.



Flujo general de telemetría
1. El simulador crea una métrica de prueba para un usuario y un pipeline.
2. FastAPI la almacena en PostgreSQL con su fecha/hora.
3. El backend envía el evento por WebSocket a la sesión autenticada de ese usuario.
4. React actualiza el dashboard y el feed sin recargar la página.
Flujo general de J.A.R.V.I.S.
1. El usuario envía una pregunta y, si existe, el contexto reciente de su conversación.
2. FastAPI valida el JWT y remite el mensaje a Groq.
3. Cuando el modelo solicita información del usuario, FastAPI ejecuta únicamente las herramientas autorizadas con el identificador de la sesión autenticada.
4. Los datos recuperados se devuelven al modelo para redactar la respuesta y React la presenta con Markdown.
5. Las hipótesis se comunican como posibles causas por verificar; el asistente no actúa directamente sobre sistemas externos.
Distinción técnica: las recomendaciones de la telemetría simulada se producen localmente; la IA se invoca para el chat, no para analizar cada registro del simulador de manera automática.
Diagrama resumido de integración
La secuencia siguiente representa el prototipo actual; no supone ingesta desde infraestructura externa:
Simulador asíncrono (FastAPI)
    -> PostgreSQL (usuarios y anomalías)
    -> WebSocket autenticado
    -> Dashboard React (gráficas y feed)

Usuario autenticado -> FastAPI /chat/ -> Groq
                                        -> solicitud de herramienta
                     FastAPI -> consulta autorizada a PostgreSQL
                     FastAPI -> resultado para Groq -> respuesta al usuario
## 6. Reglas de seguridad y uso responsable de IA
- Las rutas de anomalías y chat deben requerir autenticación; las consultas deben estar asociadas al usuario autenticado, nunca a un identificador suministrado libremente por el modelo.
- Las llamadas a herramientas de IA se restringen a funciones expresamente permitidas por FastAPI.
- Las entradas del modelo y sus parámetros deben validarse; no ejecutar SQL arbitrario generado por la IA.
- Distinguir datos realmente consultados en PostgreSQL de hipótesis técnicas.
- No afirmar que se inspeccionaron logs o sistemas externos sin haberlo hecho.
- Evitar recomendaciones destructivas basadas únicamente en métricas simuladas.
- Mantener claves JWT, SMTP, base de datos y Groq fuera del repositorio.
## 7. Plan de trabajo y evolución
- **Sprint 1 — Datos**
  - **Entregable:** Modelos y almacenamiento relacional en PostgreSQL.
  - **Estado:** Implementado.

- **Sprint 2 — Seguridad y backend**
  - **Entregable:** API, JWT, códigos SMTP y simulador asíncrono.
  - **Estado:** Implementado; pendiente de ampliar pruebas sistemáticas.

- **Sprint 3 — Interfaz y tiempo real**
  - **Entregable:** React, Recharts, WebSocket por usuario y J.A.R.V.I.S. 2.0.
  - **Estado:** Implementado y probado funcionalmente en entorno local.

- **Sprint 4 — Empaquetamiento y documentación**
  - **Entregable:** Docker Compose, README, MVP, PRD y comprobaciones de compilación.
  - **Estado:** Implementado en entorno local; revisión documental actualizada en octubre de 2026.

- **Evolución posterior**
  - **Entregable:** Conectores reales, consultas históricas avanzadas, pruebas exhaustivas de seguridad y carga, despliegue y observabilidad de producción.
  - **Estado:** Fuera del MVP / pendiente.



## 8. Criterios de aceptación

**Evidencia de validacion (octubre de 2026):** se comprobo el arranque de una copia limpia con Docker Compose y PostgreSQL. Ademas, se ejecutaron 9 pruebas automatizadas de integracion de API, autenticacion, CORS y base de datos, todas satisfactorias. Suite: `backend/tests/test_integracion_http.py`. Esto no equivale a una auditoria completa de seguridad, carga, SMTP, Groq o WebSocket.

- CA-01: FastAPI inicia correctamente y el simulador genera registros sin intervención manual.
- CA-02: el usuario autenticado recibe y visualiza sus anomalías en el dashboard mediante WebSocket.
- CA-03: el feed muestra la hora proveniente del registro de base de datos, no la hora actual del navegador.
- CA-04: J.A.R.V.I.S. contesta consultas generales y, cuando necesita datos, utiliza la herramienta autorizada para recuperar anomalías por estado del usuario.
- CA-05: las respuestas de IA separan valores observados de causas no verificadas y sugieren verificaciones seguras.
- CA-06: los mensajes largos y las tablas pueden recorrerse dentro del chat, y el botón «↓ Último» funciona sin deformar el dashboard.
- CA-07: el usuario puede consultar registros disponibles y exportar la bitácora visible a PDF.
- CA-08: la verificación de cuenta y las rutas protegidas impiden accesos no autorizados según las reglas implementadas; el backend rechaza solicitudes sin JWT y con JWT de usuarios inactivos, y las credenciales no aparecen en los archivos versionados revisados.
- CA-09: la compilación del frontend concluye sin errores y los servicios API/BD pueden ejecutarse en el entorno documentado.
- CA-10: README, MVP y PRD describen expresamente la simulación y no atribuyen capacidades productivas inexistentes.
- CA-11: desde la pantalla React de recuperación se solicita el código SMTP, se recibe en el correo registrado, se restablece la contraseña y se puede volver a iniciar sesión. Comprobado manualmente en el entorno local.
Estado de validación: se han comprobado localmente compilación, arranque de servicios y funciones clave del dashboard y del chat. También se probaron la recuperación de contraseña completa y las respuestas de autorización HTTP 401 en rutas protegidas. La aceptación académica definitiva y una eventual certificación para producción requieren pruebas adicionales y evaluación externa.
## 9. Riesgos, supuestos y restricciones
- La calidad de los diagnósticos depende de los registros entregados, del modelo y de sus límites de cuota; no existe certeza causal automática.
- La telemetría sintética sirve para demostrar flujos y no predice confiablemente incidentes empresariales reales.
- El rendimiento observado en una computadora local no equivale a la capacidad en producción.
- La memoria de chat enviada desde React es temporal y limitada.
- El sistema SMTP depende de credenciales y conectividad externas y no se emplea como canal de alerta masiva.
- Limitación de los códigos: el flujo implementado requiere el código enviado por correo y lo invalida al usarlo, pero todavía no aplica expiración temporal ni límite de intentos fallidos. No se considera un sistema de recuperación endurecido para producción.
## 10. Lista de verificación de los requisitos
- [x] Registro, verificación de cuentas, JWT y recuperación de acceso implementados.
- [x] Solicitud del código SMTP desde React, actualización de contraseña y nuevo inicio de sesión probados manualmente.
- [x] Acceso sin JWT y mediante JWT de cuenta inactiva rechazado en pruebas HTTP locales.
- [x] Simulación, almacenamiento y actualización por WebSocket implementados.
- [x] J.A.R.V.I.S. con consulta controlada de anomalías y respuesta orientativa implementado.
- [x] Lectura de tablas y desplazamiento del chat comprobados localmente.
- [ ] Pruebas automatizadas completas de autorización, carga y recuperación ante fallos.
- [ ] Integraciones de producción y remediación automática (fuera del alcance actual).
## 11. Documentos relacionados
- [`../README.md`](../README.md) — presentación, configuración y puesta en marcha.
- [`../frontend/README.md`](../frontend/README.md) — implementación y uso de la interfaz.
- [`MVP.md`](MVP.md) — alcance implementado, validaciones y exclusiones.
Conclusión: PluriOne cumple el propósito de demostrar un flujo integral de observabilidad simulada asistida por IA en un entorno local. Su arquitectura deja abierta la posibilidad de integrar fuentes reales en versiones futuras, sin afirmar que esa capacidad ya existe.
Versión documental del prototipo académico, octubre de 2026.
