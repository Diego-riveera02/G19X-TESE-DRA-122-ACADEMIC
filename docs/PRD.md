# Product Requirements Document (PRD)

**Proyecto:** Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
**Empresa:** PluriOne S.A. de C.V. (Puebla 46, CDMX)
**Autor:** Diego Rivera Aguilar
**Fecha:** Octubre de 2026

---

## 1. Propósito, Problemática y Visión General

**Problemática**
Actualmente, el monitoreo de los flujos de datos (DataOps) en las organizaciones suele ser reactivo. La identificación tardía de cuellos de botella por latencia, datos corruptos y fallos en la migración de pipelines genera interrupciones operativas, baja calidad en la toma de decisiones y una resolución ineficiente de incidentes técnicos.

**Propósito y Visión general**
Este proyecto tiene como finalidad el desarrollo de una Plataforma de Observabilidad de Datos integral para centralizar el monitoreo de salud de los pipelines corporativos. La solución integra procesamiento en tiempo real mediante WebSockets, almacenamiento persistente relacional y capacidades de inteligencia artificial (asistente J.A.R.V.I.S.) para diagnosticar anomalías de manera proactiva y automatizada.

## 2. Público Objetivo y Objetivos del Proyecto

**Público objetivo**
- **Ingenieros de Datos y DataOps:** Para supervisar en tiempo real la salud de los pipelines y recibir alertas inmediatas ante fallos críticos.
- **Lideres Técnicos y CTOs:** Para evaluar métricas globales de rendimiento, latencia y tasas de error a través de un dashboard ejecutivo.
- **Administradores del Sistema:** Para gestionar el acceso seguro de usuarios y la persistencia de las bitácoras en la base de datos corporativa.

**Objetivos**
- **Objetivo general:** Desarrollar una plataforma web de observabilidad de datos con diagnóstico automatizado por inteligencia artificial.
- **Objetivos específicos:**
  - Implementar un sistema de autenticación seguro basado en JWT y control de accesos.
  - Diseñar tableros interactivos en React con gráficos dinámicos para visualizar métricas clave.
  - Integrar WebSockets para la notificación bidireccional y en tiempo real de anomalías.
  - Habilitar la exportación de bitácoras completas de incidentes en formato PDF.

## 3. Alcance del Proyecto

**Dentro del alcance (Lo que sí se hará)**
- Monitoreo en tiempo real de pipelines de datos críticos (`api_gateway`, `pipeline_ventas_mx`, `migracion_aws`).
- Ingesta, procesamiento y almacenamiento de anomalías en una base de datos PostgreSQL.
- Desarrollo de un motor de análisis de causa raíz asistido por IA (J.A.R.V.I.S.).
- Interfaz web interactiva en React.js con visualización analítica (Recharts).
- Empaquetamiento y despliegue modular mediante contenedores (Docker Compose).

**Fuera del alcance (Lo que NO se hará)**
- El sistema no realiza modificaciones directas ni escrituras automáticas sobre las fuentes de datos productivas externas sin la validación de un operador humano.
- No se contempla el aprovisionamiento de infraestructura física local, operando exclusivamente bajo esquemas contenedorizados.

## 4. Requisitos del Producto e Historias de Usuario

**Requisitos Funcionales e Historias de Usuario**
1. Como ingeniero de datos, quiero iniciar sesión de forma segura para acceder al panel de control de la plataforma.
2. Como operador, quiero recibir notificaciones instantáneas vía WebSocket cuando una métrica de pipeline rebase los umbrales críticos.
3. Como analista, quiero consultar al asistente de IA (J.A.R.V.I.S.) sobre la causa raíz de una anomalía para acelerar la solución del incidente.
4. Como auditor, quiero exportar la bitácora de anomalías a un archivo PDF estructurado para respaldar los reportes operativos.

**Requisitos No Funcionales**
1. **Rendimiento y Tiempo Real:** Las alertas por WebSockets deben reflejarse en la interfaz en menos de un segundo tras su inyección.
2. **Seguridad:** Encriptación de credenciales y protección de endpoints mediante tokens JWT.
3. **Portabilidad:** Despliegue estandarizado de la arquitectura utilizando Docker y Docker Compose.

## 5. Arquitectura del Sistema y Tecnologías

**Stack Tecnológico**
- **Lenguaje Backend / API:** Python / FastAPI
- **Interfaz de usuario (Frontend):** React.js + Recharts
- **Base de datos relacional:** PostgreSQL
- **Comunicación en Tiempo Real:** WebSockets
- **Contenedores y Orquestación:** Docker & Docker Compose
- **Seguridad:** Autenticación JWT y Hash de contraseñas
- **Metodología de trabajo:** Ingeniería de desarrollo ágil

## 6. Arquitectura General
1. Fuentes de datos y simulación de pipelines (`api_gateway`, `ventas`, `migración`)
2. FastAPI Backend (Gestión de API y WebSockets)
3. Motor de Diagnóstico por IA (J.A.R.V.I.S.)
4. PostgreSQL (Persistencia de usuarios e historial de anomalías)
5. React.js Frontend (Dashboard interactivo y visualización)

## 7. Plan de Trabajo

1. **Detección de necesidades:** Definición de métricas clave de observabilidad (latencia, calidad, fallos).
2. **Diseño de arquitectura:** Selección del stack tecnológico (FastAPI, React, PostgreSQL, Docker).
3. **Desarrollo del Backend:** Estructuración de modelos, esquemas y endpoints principales.
4. **Desarrollo del Frontend:** Creación de componentes visuales, gráficos y paneles interactivos.
5. **Integración y Tiempo Real:** Conexión de WebSockets y motor de IA simulado.
6. **Pruebas y Validación:** Verificación de la integridad de datos y despliegue local con Docker.
7. **Documentación técnica:** Elaboración del PRD y MVP en formato Markdown para el repositorio.

## 8. Backlog del Proyecto

**Sprint 1: Fundamentos y Base de Datos**
- Configuración de la estructura del proyecto y entorno de desarrollo.
- Diseño e implementación de la conexión a PostgreSQL para el almacenamiento de registros.

**Sprint 2: Backend, API y Seguridad**
- Desarrollo de rutas RESTful en FastAPI para la gestión de anomalías y autenticación.
- Implementación de la seguridad basada en tokens de acceso.

**Sprint 3: Frontend, WebSockets e Inteligencia Artificial**
- Construcción del Dashboard interactivo en React.js con gráficas de rendimiento.
- Integración de WebSockets para alertas en tiempo real y el panel de J.A.R.V.I.S.

**Sprint 4: Contenedorización, QA y Documentación**
- Creación de archivos Dockerfile y orquestación con Docker Compose.
- Pruebas finales de integración y redacción de la documentación técnica en la carpeta `docs/`.

## 9. Criterios de Aceptación (Éxito del Proyecto)
1. Conexión exitosa y persistencia de datos validada entre la API de FastAPI y la base de datos PostgreSQL.
2. Renderizado fluido de gráficos y recepción activa de notificaciones mediante WebSockets en la interfaz de React.
3. Funcionamiento óptimo del asistente inteligente J.A.R.V.I.S. y correcta exportación de reportes en PDF.