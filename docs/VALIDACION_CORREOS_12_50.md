# Validacion de correos diferenciados - Fase 12.50

## 1. Objetivo

Documentar la correccion que permite distinguir los mensajes
de verificacion de cuenta y recuperacion de contrasena de PluriOne.

La finalidad es proporcionar informacion clara al usuario,
conservando el comportamiento de autenticacion existente.

## 2. Alcance

La correccion se concentra en la generacion de mensajes,
la seleccion de la funcion de envio y las pruebas unitarias.

No incluye cambios en el esquema de PostgreSQL, migraciones,
modificaciones de contrasenas ni nuevas funcionalidades de IA.

## 3. Archivos modificados

Los cambios funcionales se integraron en cuatro archivos:

- backend/app/auth_router.py
- backend/app/email_utils.py
- backend/app/main.py
- backend/tests/test_plantillas_correo.py

## 4. Cambios implementados

### 4.1 Verificacion de cuenta

Se conserva el comportamiento anterior para los correos
de verificacion.

El mensaje utiliza un asunto relacionado con la verificacion
de cuenta y presenta el codigo temporal correspondiente.

### 4.2 Recuperacion de contrasena

Los mensajes de recuperacion utilizan un asunto especifico.

Tambien se modifica el encabezado del contenido HTML y la
explicacion sobre el uso del codigo temporal.

La finalidad es evitar que un correo de recuperacion parezca
un mensaje de verificacion de una cuenta nueva.

### 4.3 Integracion con autenticacion

El router de autenticacion puede recibir una funcion de envio
especifica para la recuperacion de contrasena.

Se conserva una alternativa compatible con la funcion anterior
cuando no se proporciona dicha dependencia.

La aplicacion principal conecta la funcion correspondiente
mediante el proposito de recuperacion.

### 4.4 Validacion de propositos

La utilidad de correo admite los propositos esperados.

Los valores desconocidos se rechazan antes de establecer
una conexion SMTP.

## 5. Pruebas aisladas de la fase

Se realizaron comprobaciones mediante SMTP simulado.

Resultados registrados:

- 11 comprobaciones ejecutadas.
- 11 comprobaciones aprobadas.
- Asunto de verificacion correcto.
- Asunto de recuperacion correcto.
- Encabezados diferenciados.
- Ausencia de encabezados cruzados.
- Codigo ficticio presente en ambas plantillas.
- Conexion del router de recuperacion comprobada.
- Conexion desde la aplicacion principal comprobada.
- Rechazo de propositos invalidos antes de abrir SMTP.

Estas comprobaciones utilizaron datos ficticios y objetos
simulados en lugar de enviar mensajes reales.

## 6. Pruebas unitarias permanentes

Se incorporo el archivo:

backend/tests/test_plantillas_correo.py

Contiene cuatro pruebas:

1. Verificacion de cuenta con el proposito predeterminado.
2. Recuperacion de contrasena con contenido diferenciado.
3. Comparacion de los asuntos de ambos tipos de correo.
4. Rechazo de un proposito desconocido sin abrir SMTP.

Resultado local:

- 4 pruebas ejecutadas.
- 4 pruebas aprobadas.

El archivo se ejecuto con Python local porque el contenedor
existente no tenia montado el nuevo archivo durante esa prueba.

## 7. Integracion continua

El Pull Request numero 22 fue sometido a las verificaciones
configuradas en GitHub Actions.

Resultados observados:

- PluriOne CI / Backend - isolated tests: aprobado.
- PluriOne CI / Frontend - production build: aprobado.
- Sin conflictos con la rama principal.

La aprobacion del CI corresponde a los trabajos configurados
en el repositorio. Este registro no presupone que todos los
casos locales se hayan ejecutado dentro de GitHub Actions.

## 8. Trazabilidad de Git

Repositorio:

https://github.com/Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC

Pull Request:

https://github.com/Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC/pull/22

Rama de desarrollo:

fix/correos-diferenciados-12-50

Commit de correccion:

7358bc3

Commit de integracion:

c400503

Commit base:

cb56491

La integracion comprende cuatro archivos con 150 lineas
agregadas y cinco eliminadas.

## 9. Seguridad y limites de las pruebas

Las pruebas aisladas de plantillas utilizaron SMTP simulado.

No se enviaron mensajes reales durante estas pruebas.

No se modificaron contrasenas ni se realizaron operaciones
sobre PostgreSQL mediante los procedimientos de esta fase.

La entrega real de correo SMTP ya habia sido comprobada
previamente y se documento en la fase 12.49.

Sin embargo, no se realizo una nueva comprobacion de
recepcion real de ambas plantillas despues de la correccion.

Tampoco se considera demostrada mediante estas cuatro
pruebas una recuperacion completa de contrasena de extremo
a extremo.

Las 58 pruebas historicas del refactor, descritas en el
README, constituyen evidencias anteriores y no se suman
a las cuatro pruebas unitarias de esta fase.

## 10. Resultado

La diferenciacion de correos fue implementada, probada
de manera aislada e integrada mediante el Pull Request 22.

Las comprobaciones locales de las plantillas aprobaron,
y las dos verificaciones mostradas por GitHub Actions
finalizaron correctamente.

La rama principal quedo sincronizada en el commit c400503.

Queda pendiente, si se requiere como evidencia adicional,
realizar una nueva prueba controlada de entrega y recepcion
de los dos tipos de mensajes reales.

## 11. Referencias

- README.md del repositorio.
- docs/VALIDACION_SMTP_12_49.md.
- backend/tests/test_plantillas_correo.py.
- Pull Request 22 y sus comprobaciones de GitHub Actions.
