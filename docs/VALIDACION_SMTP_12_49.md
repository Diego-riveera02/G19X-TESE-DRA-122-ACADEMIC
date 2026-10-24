# Evidencias de validacion SMTP - Fase 12.49

## 1. Identificacion

- Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial.
- Empresa de referencia: PluriOne S.A. de C.V.
- Repositorio: G19X-TESE-DRA-122-ACADEMIC.
- Fecha de validacion: 24 de octubre de 2026.
- Corte: Cuarto corte academico.
- Commit base de las pruebas: 82d54c2e90db1b95db6d6790f64604114d93cf09.

## 2. Objetivo

Verificar la configuracion SMTP de PluriOne y comprobar
la generacion, el envio y la recepcion de correos asociados
con el proceso de recuperacion de contrasena.

Las pruebas se realizaron utilizando la API local en Docker,
PostgreSQL y una cuenta verificada del propio sistema.

No se publicaron credenciales, contrasenas ni codigos reales.

## 3. Entorno utilizado

- Backend: FastAPI.
- Base de datos: PostgreSQL.
- Contenedores: Docker Compose.
- Servicio de correo: Gmail SMTP.
- Servidor SMTP: smtp.gmail.com.
- Puerto: 587.
- Seguridad de transporte: STARTTLS.
- API local: http://127.0.0.1:8000.

Durante las comprobaciones, los servicios api y db
se encontraron en funcionamiento.

## 4. Prueba 12.49.1 - Configuracion y conectividad

Se verifico la disponibilidad de las variables SENDER_EMAIL
y SENDER_PASSWORD dentro del contenedor de la API.

Ambas variables estaban configuradas.

Tambien se comprobo que el contenedor podia establecer
una conexion TCP con smtp.gmail.com en el puerto 587.

Resultado: satisfactorio.

No se imprimieron los valores de las credenciales.

## 5. Prueba 12.49.2 - Autenticacion SMTP

Se establecio una conexion con Gmail SMTP y se inicio
una sesion cifrada mediante STARTTLS.

El servidor acepto las credenciales configuradas.

Resultado: autenticacion SMTP aprobada.

Esta prueba no envio correos.

## 6. Prueba 12.49.3 - Envio SMTP directo

Se envio un mensaje de diagnostico desde la cuenta
remitente configurada hacia la misma cuenta.

Identificador tecnico:

20261024-230915-3E9E93

Gmail acepto el mensaje y el usuario confirmo su recepcion.

Resultado: envio y recepcion satisfactorios.

## 7. Prueba 12.49.4 - Estado de la cuenta

Se consulto mediante SQLAlchemy el estado de una cuenta
registrada en PluriOne.

Se confirmo que la cuenta existia, estaba verificada
y no tenia una recuperacion vigente al momento de la consulta.

Resultado: cuenta apta para solicitar recuperacion.

La consulta fue de solo lectura.

## 8. Prueba 12.49.5 - Solicitud de recuperacion

Se utilizo el endpoint:

POST /solicitar-recuperacion/

La API recibio correctamente una solicitud para la cuenta
verificada y devolvio la respuesta generica prevista
para evitar revelar informacion sobre usuarios.

El endpoint no cambio la contrasena.

La solicitud si genero un estado temporal de recuperacion
en PostgreSQL, tal como requiere el funcionamiento normal.

Resultado: solicitud HTTP aceptada.

## 9. Prueba 12.49.6 - Persistencia temporal

Se realizo una consulta de solo lectura para verificar
el estado posterior a la solicitud.

Resultados observados:

- Cuenta encontrada: verdadero.
- Cuenta verificada: verdadero.
- Solicitud de recuperacion: verdadero.
- Codigo vigente: verdadero.
- Tiempo restante aproximado: 417 segundos.

No se detectaron errores SMTP mediante los indicadores
examinados en los registros recientes del contenedor.

Resultado: estado temporal de recuperacion confirmado.

La ausencia de errores registrados, por si sola,
no representa una confirmacion de entrega.

## 10. Prueba 12.49.7 - Entrega al correo registrado

Se envio un unico correo de diagnostico directamente
a la direccion registrada en PluriOne.

Identificador tecnico:

20261024-232809-AF797E

El servidor SMTP acepto el correo.

El usuario confirmo que el mensaje llego a su cuenta
aproximadamente a las 17:28, hora de Mexico.

Resultado: entrega SMTP directa satisfactoria.

No se genero otro codigo de recuperacion.

## 11. Prueba 12.49.8 - Plantilla HTML

Se ejecuto directamente la funcion de correo HTML
utilizada por el backend.

Se empleo exclusivamente el valor ficticio 000000,
que no constituye un codigo real de recuperacion.

El servidor SMTP acepto el mensaje.

El usuario confirmo que el correo con el valor ficticio
llego aproximadamente a las 17:31, hora de Mexico.

Resultado: plantilla HTML aceptada y recibida.

## 12. Prueba 12.49.9 - Correo de recuperacion

Al revisar la bandeja de Gmail, se identifico
un mensaje de PluriOne recibido aproximadamente
a las 17:20, hora de Mexico.

El usuario confirmo que dicho mensaje contenia
un codigo de seis digitos diferente del valor ficticio
000000 utilizado en la prueba posterior.

El horario y el tipo de mensaje son compatibles
con la solicitud realizada mediante el endpoint
de recuperacion.

Resultado: recepcion manual del mensaje de recuperacion
confirmada por el usuario, con correlacion temporal.

Por seguridad, el codigo real no se recopilo
ni se incorporo a este documento.

## 13. Resultados generales

Las comprobaciones proporcionaron evidencia favorable de:

- Configuracion de credenciales SMTP.
- Conectividad con Gmail.
- Autenticacion mediante STARTTLS.
- Envio SMTP directo.
- Recepcion en una cuenta registrada.
- Disponibilidad del endpoint de recuperacion.
- Persistencia temporal de una solicitud de recuperacion.
- Envio y recepcion de la plantilla HTML.
- Recepcion de un mensaje compatible con la solicitud real.

El repositorio permanecio sin modificaciones durante
la ejecucion de las pruebas de diagnostico.

Los servicios principales continuaron funcionando.

## 14. Limitaciones y pendientes

La prueba no incluyo la ejecucion del endpoint
POST /recuperar-password/ con un codigo real.

Por tanto, no se afirma que el cambio efectivo
de contrasena haya sido validado en este procedimiento.

Tampoco se comprobo mediante una traza automatizada
la entrega de cada tarea de correo en segundo plano.

Se identifico una mejora de experiencia de usuario:
los mensajes de verificacion de cuenta y recuperacion
utilizan actualmente el mismo asunto y plantilla.

Se recomienda distinguir ambos tipos de correo
en una correccion posterior, acompanada de pruebas.

No se incorporaron capturas completas de la bandeja
porque contienen mensajes personales ajenos al proyecto.

## 15. Conclusion

La fase 12.49 permitio comprobar que PluriOne dispone
de una configuracion SMTP funcional y puede entregar
correos a una cuenta registrada.

Tambien se obtuvo evidencia de una solicitud real de
recuperacion almacenada temporalmente y de la recepcion
de un mensaje compatible con dicha solicitud.

La modificacion de contrasenas queda fuera del alcance
de estas pruebas para preservar la cuenta utilizada.

La mejora prioritaria identificada consiste en diferenciar
los mensajes de verificacion y recuperacion para evitar
confusiones durante el uso de la plataforma.
