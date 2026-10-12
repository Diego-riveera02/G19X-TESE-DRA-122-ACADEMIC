# Product Minimum Viable (MVP)

**Proyecto:** Plataforma de Observabilidad de Datos con Inteligencia Artificial (PluriOne)
**Autor:** Diego Rivera Aguilar
**Fecha:** Octubre de 2026

---

## 1. Alcance del MVP

El Producto Mínimo Viable (MVP) de PluriOne se centra en entregar un software completamente funcional que valida el ciclo completo de observabilidad de datos: desde la recepción de métricas hasta la visualización y el diagnóstico inteligente.

- **Módulo de Autenticación:** Control de acceso mediante usuarios registrados y tokens de sesión.
- **Monitoreo y Alertas en Tiempo Real:** Detección de anomalías en pipelines mediante eventos dinámicos y WebSockets.
- **Dashboard Analítico:** Gráficas interactivas para el análisis de latencia, calidad de datos y porcentajes de fallo.
- **Asistente de Diagnóstico (J.A.R.V.I.S.):** Módulo interactivo de IA para la recomendación de soluciones ante eventos críticos.
- **Exportación de Bitácoras:** Funcionalidad para la descarga de reportes operativos en formato PDF.

## 2. Estado de Desarrollo del MVP

- [x] Configuración de la base de datos relacional en PostgreSQL.
- [x] Desarrollo de la API de backend con FastAPI y rutas de autenticación.
- [x] Implementación de la comunicación en tiempo real mediante WebSockets.
- [x] Desarrollo del frontend moderno en React.js con componentes de visualización.
- [x] Empaquetamiento y pruebas de ejecución local mediante Docker Compose.

## 3. Criterios de Validación del MVP

1. **Eficiencia en la Comunicación:** Los eventos de alerta viajan por WebSockets y se muestran en el dashboard sin recargar la página.
2. **Consistencia de Datos:** La base de datos PostgreSQL almacena y recupera los registros de manera íntegra.
3. **Experiencia de Usuario:** La interfaz gráfica en React permite alternar de forma fluida entre el monitoreo general y el panel de consultas con IA.