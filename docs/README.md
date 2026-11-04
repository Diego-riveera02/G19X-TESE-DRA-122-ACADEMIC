# Índice técnico de documentación — PluriOne

**Proyecto:** Plataforma de Observabilidad de Datos con Inteligencia Artificial.

**Autor:** Diego Rivera Aguilar.

**Revisión:** Corte 7 de TODO Academy, noviembre de 2026.

**Referencia base:** `c3bdcc3`.

## 1. Propósito

Este índice permite identificar los documentos principales del
proyecto, distinguir las pruebas históricas de las verificaciones
posteriores y localizar las evidencias técnicas disponibles.

Las fechas y los commits de la tabla corresponden a la última
modificación publicada de cada archivo antes de las correcciones
documentales del Corte 7.

## 2. Índice de documentos

| Documento | Última publicación | Commit | Clasificación | Contenido |
| --- | --- | --- | --- | --- |
| [PRD.md](PRD.md) | 2026-10-29 | `2872b92` | Referencia principal | Requisitos, alcance y arquitectura del producto. |
| [MVP.md](MVP.md) | 2026-10-29 | `2872b92` | Referencia principal | Funciones implementadas, límites y pendientes del MVP. |
| [INSTALACION_LITERAL_CORTE5.md](INSTALACION_LITERAL_CORTE5.md) | 2026-10-29 | `c3bdcc3` | Actual con antecedentes históricos | Instalación original del Corte 5, validación integral posterior del Corte 6 e investigación del HTTP 401. |
| [EVIDENCIAS_FUNCIONALES_CORTE6.md](EVIDENCIAS_FUNCIONALES_CORTE6.md) | 2026-10-29 | `6a6bf0c` | Seguimiento del Corte 6 | Pruebas funcionales, autenticación, métricas, alertas y captura HTTP 200. |
| [PRUEBA_E2E_CORTE4.md](PRUEBA_E2E_CORTE4.md) | 2026-10-24 | `20b8443` | Histórico | Primera evidencia de prueba de extremo a extremo. |
| [VALIDACION_CLON_LIMPIO_CORTE4.md](VALIDACION_CLON_LIMPIO_CORTE4.md) | 2026-10-24 | `671343d` | Histórico | Validación de instalación desde un clon del Corte 4. |
| [VALIDACION_CORREOS_12_50.md](VALIDACION_CORREOS_12_50.md) | 2026-10-24 | `71b179c` | Histórico | Pruebas de correos diferenciados. |
| [VALIDACION_E2E_CLON_CORTE4.md](VALIDACION_E2E_CLON_CORTE4.md) | 2026-10-25 | `1220469` | Histórico | Recorrido funcional desde un clon aislado del Corte 4. |
| [VALIDACION_MAILPIT_CORTE5.md](VALIDACION_MAILPIT_CORTE5.md) | 2026-10-27 | `9c16e74` | Histórico | Validación del correo local mediante Mailpit. |
| [VALIDACION_RECUPERACION_MAILPIT_CORTE4.md](VALIDACION_RECUPERACION_MAILPIT_CORTE4.md) | 2026-10-25 | `7f6e6d7` | Histórico | Pruebas de recuperación de contraseña. |
| [VALIDACION_SMTP_12_49.md](VALIDACION_SMTP_12_49.md) | 2026-10-24 | `66ca590` | Histórico | Validación de la configuración SMTP. |
| [VALIDACION_TECNICA_12_48.md](VALIDACION_TECNICA_12_48.md) | 2026-10-24 | `1308829` | Histórico | Comprobaciones técnicas de la fase 12.48. |

## 3. ¿Qué documento debo consultar primero?

Para conocer los requisitos y el alcance, consultar `PRD.md`
y `MVP.md`.

Para reproducir el proyecto, comenzar con el `README.md`
principal del repositorio y utilizar
`INSTALACION_LITERAL_CORTE5.md` como bitácora de referencia.

La sección 12 de esa bitácora describe una instalación
posterior desde un clon nuevo con registro, verificación,
primer login HTTP 200, pipeline, ingesta HTTP 201 y alerta.

La sección 13 documenta un mecanismo reproducible de
HTTP 401. No demuestra la causa exacta del incidente
histórico del Corte 5.

Para revisar pruebas funcionales y la captura publicada
del login HTTP 200, consultar
`EVIDENCIAS_FUNCIONALES_CORTE6.md`.

## 4. Evidencia gráfica disponible

Los archivos gráficos publicados incluyen:

- [Login HTTP 200](evidencias/login_http200_main_20261029.png)
- [Alerta E2E desde clon](evidencias/alerta_e2e_clon_1253.jpeg)
- [Alerta E2E del Corte 4](evidencias/alerta_e2e_corte4.jpeg)
- [Recuperación con código vencido](evidencias/recuperacion_codigo_vencido_mailpit_1254.jpeg)

Las capturas históricas no se presentan como evidencia
visual nueva de la instalación integral del Corte 6.

## 5. Criterio de vigencia

Los documentos históricos se conservan como evidencia de
las pruebas realizadas en sus respectivos cortes.

Los documentos de referencia principal y seguimiento
contienen información posterior, pero deben interpretarse
según las fechas y commits que registran.

La validación integral del Corte 6 no elimina el hecho
de que durante el Corte 5 ocurrió un HTTP 401.

Las correcciones del Corte 7 se publicarán en un nuevo
commit. Este índice no sustituye la verificación técnica
del repositorio ni la ejecución de sus pruebas.
