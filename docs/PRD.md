Documento de Requisitos del Producto (PRD)
Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
Empresa: PluriOne S.A. de C.V. (Puebla 46, CDMX)
Autor: Diego Rivera Aguilar
Fecha: Octubre de 2026

1. Propósito, Problemática y Visión General
Problemática
Actualmente, el monitoreo de los flujos de datos (DataOps) en las organizaciones suele ser reactivo. La identificación tardía de cuellos de botella por latencia, datos corruptos y fallos en la migración de pipelines genera interrupciones operativas, baja calidad en la toma de decisiones y una resolución ineficiente de incidentes técnicos.

Propósito y Visión general
Este proyecto tiene como finalidad el desarrollo de una Plataforma de Observabilidad de Datos integral para centralizar el monitoreo de salud de los pipelines corporativos. La solución integra procesamiento en tiempo real mediante WebSockets, almacenamiento persistente relacional y capacidades de inteligencia artificial (asistente J.A.R.V.I.S.) para diagnosticar anomalías de manera proactiva y automatizada.

2. Público Objetivo y Objetivos del Proyecto
Público objetivo

Ingenieros de Datos y DataOps: Para supervisar en tiempo real la salud de los pipelines y recibir alertas inmediatas ante fallos críticos.

Lideres Técnicos y CTOs: Para evaluar métricas globales de rendimiento, latencia y tasas de error a través de un dashboard ejecutivo.

Administradores del Sistema: Para gestionar el acceso seguro de usuarios mediante validación por correo electrónico y la persistencia de las bitácoras en la base de datos corporativa.

Objetivos

Objetivo general: Desarrollar una plataforma web de observabilidad de datos con diagnóstico automatizado por inteligencia artificial y un módulo robusto de autenticación segura.

Objetivos específicos:

Implementar un sistema de autenticación seguro basado en JWT, contraseñas encriptadas con bcrypt, control de estado activo (is_active) y verificación de cuentas mediante un código único de 6 dígitos enviado por correo electrónico (SMTP).

Habilitar un flujo seguro de recuperación de credenciales por correo electrónico.

Diseñar tableros interactivos en React con gráficos dinámicos para visualizar métricas clave.

Integrar WebSockets para la notificación bidireccional y en tiempo real de anomalías.

Habilitar la exportación de bitácoras completas de incidentes en formato PDF.

3. Alcance del Proyecto
Dentro del alcance (Lo que sí se hará)

Módulo completo de registro de ingenieros con validación de identidad obligatoria vía SMTP (código de 6 dígitos).

Monitoreo en tiempo real de pipelines de datos críticos (api_gateway, pipeline_ventas_mx, migracion_aws).

Ingesta, procesamiento y almacenamiento de anomalías y usuarios en una base de datos PostgreSQL.

Desarrollo de un motor de análisis de causa raíz asistido por IA (J.A.R.V.I.S.).

Interfaz web interactiva en React.js con visualización analítica (Recharts).

Guía interactiva flotante (Onboarding) para la orientación de nuevos usuarios en el panel.

Empaquetamiento y despliegue modular mediante contenedores (Docker Compose).

Fuera del alcance (Lo que NO se hará)

El sistema no realiza modificaciones directas ni escrituras automáticas sobre las fuentes de datos productivas externas sin la validación de un operador humano.

No se contempla el aprovisionamiento de infraestructura física local, operando exclusivamente bajo esquemas contenedorizados.

4. Requisitos del Producto e Historias de Usuario
Requisitos Funcionales e Historias de Usuario

Como nuevo ingeniero, quiero registrarme ingresando mis datos y recibir un código de verificación de 6 dígitos en mi correo para activar mi cuenta de forma segura.

Como usuario registrado, quiero iniciar sesión con mis credenciales protegidas una vez que mi cuenta haya sido verificada.

Como operador, quiero recibir notificaciones instantáneas vía WebSocket cuando una métrica de pipeline rebase los umbrales críticos.

Como analista, quiero consultar al asistente de IA (J.A.R.V.I.S.) sobre la causa raíz de una anomalía para acelerar la solución del incidente.

Como auditor, quiero exportar la bitácora de anomalías a un archivo PDF estructurado para respaldar los reportes operativos.

Como usuario nuevo, quiero ver una tarjeta flotante de asistencia (J.A.R.V.I.S.) al iniciar sesión, para entender cómo interpretar las métricas sin saturar mi vista.

Requisitos No Funcionales

Rendimiento y Tiempo Real: Las alertas por WebSockets deben reflejarse en la interfaz en menos de un segundo tras su inyección.

Seguridad: Encriptación robusta de credenciales (bcrypt), protección de endpoints mediante tokens JWT y validación obligatoria de correos activos (is_active).

Portabilidad: Despliegue estandarizado de la arquitectura utilizando Docker y Docker Compose.

UI/UX: La guía de introducción debe ser un componente no intrusivo y fácil de cerrar.

5. Arquitectura del Sistema y Tecnologías
Stack Tecnológico

Lenguaje Backend / API: Python / FastAPI

Interfaz de usuario (Frontend): React.js + Recharts

Base de datos relacional: PostgreSQL

Comunicación en Tiempo Real: WebSockets

Servicio de Correo Electrónico: SMTP (Gmail API) para alertas y verificación

Contenedores y Orquestación: Docker & Docker Compose

Seguridad: Autenticación JWT, cifrado bcrypt y validación de estados de usuario

Metodología de trabajo: Ingeniería de desarrollo ágil

6. Arquitectura General
Fuentes de datos y simulación de pipelines (api_gateway, ventas, migración)

FastAPI Backend (Gestión de API, WebSockets y envío SMTP)

Motor de Diagnóstico por IA (J.A.R.V.I.S.)

PostgreSQL (Persistencia de usuarios, estados de activación y historial de anomalías)

React.js Frontend (Dashboard interactivo y visualización)

7. Plan de Trabajo
Detección de necesidades: Definición de métricas clave de observabilidad y requisitos estrictos de seguridad y control de acceso.

Diseño de arquitectura: Selección del stack tecnológico (FastAPI, React, PostgreSQL, Docker y SMTP).

Desarrollo del Backend: Estructuración de modelos de base de datos (users, anomaly_logs), esquemas y endpoints de seguridad y verificación.

Desarrollo del Frontend: Creación de componentes visuales, pantallas de autenticación, verificación por código, gráficos y paneles interactivos.

Integración y Tiempo Real: Conexión de WebSockets y motor de IA simulado.

Pruebas y Validación: Verificación de la integridad de datos, envío de correos de activación y despliegue local con Docker.

Documentación técnica: Elaboración del PRD y MVP en formato Markdown para el repositorio.

8. Backlog del Proyecto
Sprint 1: Fundamentos y Base de Datos

Configuración de la estructura del proyecto y entorno de desarrollo.

Diseño e implementación de los modelos relacionales en PostgreSQL para usuarios (con campos de activación y códigos) y registros de anomalías.

Sprint 2: Backend, API y Seguridad

Desarrollo de rutas RESTful en FastAPI para la gestión de anomalías, registro, inicio de sesión seguro, recuperación de contraseñas y el servicio de envío de códigos por correo (SMTP).

Implementación de la seguridad basada en tokens de acceso y restricciones de estado activo.

Sprint 3: Frontend, WebSockets e Inteligencia Artificial

Construcción del Dashboard interactivo en React.js con gráficas de rendimiento.

Integración de WebSockets para alertas en tiempo real y el panel de J.A.R.V.I.S.

Implementación del componente flotante de Onboarding en la pantalla principal.

Sprint 4: Contenedorización, QA y Documentación

Creación de archivos Dockerfile y orquestación con Docker Compose.

Pruebas finales de integración de extremo a extremo y redacción de la documentación técnica en la carpeta 'docs/'.

9. Criterios de Aceptación (Éxito del Proyecto)
Conexión exitosa y persistencia de datos validada entre la API de FastAPI y la base de datos PostgreSQL, incluyendo el manejo seguro de usuarios verificados por código SMTP.

Renderizado fluido de gráficos y recepción activa de notificaciones mediante WebSockets en la interfaz de React.

Funcionamiento óptimo del asistente inteligente J.A.R.V.I.S. y correcta exportación de reportes en PDF.