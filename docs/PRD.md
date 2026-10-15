# Documento de Requisitos del Producto (PRD)
Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
Empresa: PluriOne S.A. de C.V.
Autor: Diego Rivera Aguilar
Fecha: Octubre de 2026

## 1. Propósito, Problemática y Visión General
**Problemática**
Actualmente, el monitoreo de los flujos de datos (DataOps) en las organizaciones suele ser reactivo. La identificación tardía de cuellos de botella por latencia, datos corruptos y fallos en la migración de pipelines genera interrupciones operativas, baja calidad en la toma de decisiones y una resolución ineficiente de incidentes técnicos.

**Propósito y Visión general**
Este proyecto tiene como finalidad el desarrollo de una Plataforma de Observabilidad de Datos integral para centralizar el monitoreo de salud de los pipelines corporativos. La solución integra procesamiento continuo automático, almacenamiento persistente relacional y capacidades de inteligencia artificial (asistente J.A.R.V.I.S.) para diagnosticar anomalías de manera proactiva y automatizada.

## 2. Público Objetivo y Objetivos del Proyecto
**Público objetivo**
- **Ingenieros de Datos y DataOps:** Para supervisar en tiempo real la salud de los pipelines y detectar fallos críticos en vivo.
- **Lideres Técnicos y CTOs:** Para evaluar métricas globales de rendimiento, latencia y tasas de error a través de un dashboard ejecutivo.
- **Administradores del Sistema:** Para gestionar el acceso seguro de usuarios mediante validación por correo electrónico y la persistencia de las bitácoras.

**Objetivos específicos:**
- Implementar un sistema de autenticación seguro basado en JWT, contraseñas encriptadas con bcrypt y verificación de cuentas mediante un código de 6 dígitos enviado por correo electrónico (SMTP).
- Construir un motor de ingesta automática en el backend que simule el flujo constante de datos productivos, eliminando acciones manuales en el frontend.
- Diseñar tableros interactivos en React con gráficos dinámicos actualizados vía WebSockets.
- Habilitar la exportación de bitácoras completas de incidentes en formato PDF.

## 3. Alcance del Proyecto
**Dentro del alcance (Lo que sí se hará)**
- Módulo completo de registro de ingenieros con validación de identidad obligatoria vía SMTP.
- Desarrollo de un motor asíncrono en FastAPI para la generación e inyección automática de telemetría (latencia, datos corruptos, fallos) en segundo plano.
- Transmisión en tiempo real de anomalías hacia el frontend mediante WebSockets.
- Desarrollo de un motor de análisis de causa raíz asistido por IA (J.A.R.V.I.S.).
- Interfaz web interactiva en React.js con visualización analítica (Recharts).

**Fuera del alcance (Lo que NO se hará)**
- El sistema no realiza modificaciones directas ni escrituras automáticas sobre las fuentes de datos productivas externas.
- El servicio SMTP no se utilizará para emitir notificaciones por cada anomalía detectada en el motor continuo, evitando así el bloqueo de la cuenta por envío masivo (SPAM); su uso es estrictamente de seguridad y autenticación.

## 4. Requisitos del Producto e Historias de Usuario
**Requisitos Funcionales e Historias de Usuario**
- Como nuevo ingeniero, quiero registrarme e ingresar el código de verificación de 6 dígitos enviado a mi correo para activar mi cuenta de forma segura.
- Como sistema backend, quiero generar y transmitir métricas automáticamente en segundo plano para reflejar el comportamiento de un entorno de producción real, sin requerir clics manuales.
- Como operador, quiero ver cómo las gráficas de mi dashboard se actualizan solas y en tiempo real vía WebSocket.
- Como analista, quiero consultar al asistente de IA (J.A.R.V.I.S.) sobre la causa raíz de una anomalía para acelerar la solución del incidente.

**Requisitos No Funcionales**
- **Rendimiento:** El motor automático debe generar métricas cada 5 segundos y los WebSockets deben reflejarlas inmediatamente en la interfaz.
- **Seguridad:** Encriptación robusta (bcrypt), tokens JWT, restricción SMTP exclusiva para identidad y variables protegidas en archivos `.env`.

## 5. Arquitectura del Sistema y Tecnologías
**Stack Tecnológico**
- **Lenguaje Backend / API:** Python / FastAPI
- **Interfaz de usuario (Frontend):** React.js + Recharts
- **Base de datos relacional:** PostgreSQL
- **Comunicación en Tiempo Real:** WebSockets
- **Servicio de Correo Electrónico:** SMTP (Gmail API) con uso restringido a seguridad (login/recuperación).
- **Contenedores:** Docker & Docker Compose

## 6. Arquitectura General
1. Motor de Ingesta Automática Asíncrono (Simulador de Telemetría).
2. FastAPI Backend (Gestión de API, WebSockets y envío SMTP seguro).
3. Motor de Diagnóstico por IA (J.A.R.V.I.S.).
4. PostgreSQL (Persistencia de usuarios, estados y anomalías).
5. React.js Frontend (Dashboard interactivo sin botones de inyección manual).

## 7. Plan de Trabajo
- **Sprint 1 (Base de Datos):** Configuración PostgreSQL y modelos relacionales (usuarios y anomalías).
- **Sprint 2 (Seguridad y Backend):** API RESTful, encriptación, validación SMTP para cuentas e implementación del motor asíncrono de telemetría automática.
- **Sprint 3 (Frontend y Tiempo Real):** Dashboard en React.js, WebSockets, conexión de J.A.R.V.I.S y eliminación de triggers manuales.
- **Sprint 4 (Contenedores):** Docker Compose, pruebas QA y documentación técnica.

## 8. Criterios de Aceptación (Éxito del Proyecto)
- El servidor FastAPI arranca su motor de inyección de datos de manera autónoma en segundo plano.
- Los gráficos en React se actualizan automáticamente mediante WebSockets sin interacción del usuario.
- El sistema restringe exitosamente la creación de cuentas mediante verificación SMTP, manteniendo el flujo de correos libre de spam operativo.