# Evidencias funcionales del Corte 6 - PluriOne

## Entorno de pruebas

Proyecto: PluriOne - Plataforma de Observabilidad de Datos con IA.
Version comprobada: 42a49d1.
Entorno: clon aislado del Corte 5, actualizado al Corte 6.
API: http://127.0.0.1:8005
Frontend: http://127.0.0.1:5176
Mailpit: http://127.0.0.1:8026
PostgreSQL: volumen independiente del proyecto original.

## Pruebas realizadas

1. Registro de usuario nuevo: correcto.
2. Recepcion del codigo de verificacion en Mailpit: correcta.
3. Activacion de cuenta: correcta.
4. Inicio de sesion sin recuperar contrasena: correcto.
5. Creacion del pipeline pipeline-corte6-latencia: correcta.
6. Envio de latencia_ms = 9500 a /metricas/externas: HTTP 201.
7. Alerta critica visible en el Dashboard: confirmada.
8. Registro de la anomalia en Historial, fila #8: confirmado.

## Resultado

El flujo funcional de autenticacion, ingesta de metricas
externas, deteccion y consulta de alertas fue comprobado
en el entorno aislado actualizado al Corte 6.

## Evidencia visual

Se obtuvieron capturas del registro, verificacion, inicio
de sesion, pipeline, Dashboard e Historial.

Pendiente: incorporar al repositorio capturas sin credenciales,
claves de ingesta ni otros datos sensibles.

## Limitaciones y pendientes

Esta demostracion utilizo un clon existente actualizado,
no una instalacion nueva desde cero del commit 42a49d1.

La causa exacta del HTTP 401 reportado anteriormente
no ha sido determinada mediante esta prueba.

Quedan pendientes las verificaciones finales de instalacion,
seguridad y los requisitos restantes de TODO Academy.

No se incluyen contrasenas, codigos ni claves de ingesta.