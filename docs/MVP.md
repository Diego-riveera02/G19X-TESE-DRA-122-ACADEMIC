# Producto Mínimo Viable (MVP)
Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
Autor: Diego Rivera Aguilar
Fecha: Octubre de 2026

## 1. Alcance del MVP
El Producto Mínimo Viable (MVP) de PluriOne se centra en entregar un software completamente funcional que valida el ciclo completo de observabilidad de datos: desde la recepción de métricas hasta la visualización y el diagnóstico inteligente.

* **Módulo de Autenticación y Seguridad:** Control de acceso robusto mediante registro de ingenieros, encriptación de credenciales con bcrypt, verificación obligatoria de cuenta por correo electrónico (vía SMTP con un código único de 6 dígitos), control de estado activo/inactivo (is_active) en la base de datos y un flujo seguro de recuperación de contraseña.
* **Monitoreo y Alertas en Tiempo Real:** Detección de anomalías en pipelines mediante eventos dinámicos y WebSockets.
* **Dashboard Analítico:** Gráficas interactivas para el análisis de latencia, calidad de datos y porcentajes de fallo.
* **Asistente de Diagnóstico (J.A.R.V.I.S.):** Módulo interactivo de IA para la recomendación de soluciones ante eventos críticos.
* **Asistente de Onboarding (J.A.R.V.I.S.):** Implementación de un cuadro flotante en la pantalla de inicio para saludar al usuario y ofrecer una guía rápida de interpretación de telemetría.
* **Exportación de Bitácoras:** Funcionalidad para la descarga de reportes operativos en formato PDF.

## 2. Estado de Desarrollo del MVP
[x] Configuración de la base de datos relacional en PostgreSQL.

[x] Desarrollo de la API de backend con FastAPI, rutas de autenticación, verificación por SMTP y recuperación de accesos.

[x] Implementación de la comunicación en tiempo real mediante WebSockets.

[x] Desarrollo del frontend moderno en React.js con componentes de visualización y enrutamiento dinámico.

[x] Integración de la guía interactiva flotante (Onboarding) en el inicio.

[ ] Empaquetamiento y pruebas de ejecución local mediante Docker Compose.

## 3. Criterios de Validación del MVP
* **Seguridad y Activación:** El sistema restringe el acceso a usuarios no verificados mediante un flujo de código de 6 dígitos por correo, garantizando la autenticidad y seguridad de cada cuenta registrada.
* **Eficiencia en la Comunicación:** Los eventos de alerta viajan por WebSockets y se muestran en el dashboard sin recargar la página.
* **Consistencia de Datos:** La base de datos PostgreSQL almacena y recupera los registros de usuarios y métricas de manera íntegra.
* **Experiencia de Usuario:** La interfaz gráfica en React permite alternar de forma fluida entre el monitoreo general, la guía flotante y el panel de consultas con IA.