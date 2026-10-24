# Evidencias tecnicas de validacion - fase 12.48

## Identificacion

- Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial.
- Organizacion de referencia: PluriOne.
- Repositorio: Diego-riveera02/G19X-TESE-DRA-122-ACADEMIC.
- Fecha de las verificaciones: 24 de octubre de 2026.
- Commit base: 5cfb5ff12b5ce7f23203b0224c130d2905de5780.
- Alcance: instalacion limpia, Docker, frontend y autenticacion.

Este documento resume verificaciones realizadas localmente sobre el
codigo del repositorio. Los resultados locales no sustituyen las
verificaciones automaticas de GitHub Actions ni una auditoria de seguridad.

## 1. Instalacion limpia desde GitHub

Se creo un clon temporal de la rama main directamente desde GitHub.

Se verificaron:

- La coincidencia del commit local y remoto.
- La limpieza del arbol de trabajo.
- La disponibilidad de docker-compose.yml.
- La presencia de los Dockerfile del backend y frontend.
- La disponibilidad de requirements.txt y package-lock.json.
- La existencia de los archivos .env.example.
- La ausencia de archivos .env privados en el clon.

El clon se utilizo para construir imagenes independientes de prueba.

## 2. Construccion y verificacion de imagenes

Se construyeron las siguientes imagenes Docker:

- plurione-clean-api:12-48-3.
- plurione-clean-frontend:12-48-3.

La construccion se realizo desde el clon limpio.

Se verificaron mediante SHA256 los siguientes archivos
entre las imagenes y el clon:

- backend/app/main.py.
- backend/app/auth_router.py.
- frontend/package-lock.json.
- frontend/src/App.jsx.

Las comprobaciones de los cuatro archivos fueron satisfactorias.

## 3. Comprobaciones HTTP y frontend

Se utilizaron contenedores temporales independientes para comprobar
la comunicacion entre frontend y backend.

Durante el diagnostico se identifico que Vite rechazaba el nombre
interno frontend mediante HTTP 403.

Se comprobo que el acceso por IP respondia HTTP 200.

Para la prueba temporal se autorizo exclusivamente el nombre interno
frontend mediante la configuracion de Vite.

Posteriormente se comprobo que:

- La API temporal respondia HTTP 200.
- El frontend temporal respondia HTTP 200.
- React utilizaba la URL de la API temporal.
- Los puertos se publicaban exclusivamente en 127.0.0.1.

No se realizo una modificacion permanente del codigo por este
diagnostico.

## 4. Comprobaciones visuales del navegador

Se realizaron seis comprobaciones manuales satisfactorias:

1. Visualizacion de la pagina inicial.
2. Apertura del formulario de inicio de sesion.
3. Apertura del formulario de registro.
4. Validaciones de campos obligatorios.
5. Mensaje de error ante un inicio de sesion invalido.
6. Proteccion visual del dashboard sin una sesion valida.

Resultado: seis comprobaciones visuales satisfactorias.

Estas comprobaciones fueron manuales y no representan una suite
automatizada de pruebas de navegador.

## 5. Pruebas aisladas de autenticacion

Se ejecuto el router de autenticacion contra una base de datos
PostgreSQL 16 temporal.

El correo electronico y la emision de JWT se sustituyeron por
funciones controladas de prueba.

Se aprobaron 14 verificaciones, incluyendo:

- Registro de usuario ficticio.
- Rechazo de cuentas sin verificar.
- Rechazo de codigos incorrectos.
- Activacion mediante codigo valido.
- Rechazo de reutilizacion del codigo.
- Inicio de sesion valido e invalido.
- Comprobacion de JWT temporal.
- Solicitud y aplicacion de recuperacion de contrasena.
- Invalidacion de la contrasena anterior.
- Acceso con la nueva contrasena.

Resultado: 14 verificaciones satisfactorias.

No se enviaron mensajes SMTP reales.

## 6. Integracion de autenticacion con FastAPI

Se ejecuto la aplicacion real definida en backend/app/main.py
utilizando PostgreSQL temporal.

Se mantuvieron reales:

- La generacion de JWT del proyecto.
- La dependencia de autenticacion de FastAPI.
- La validacion de JWT.
- La consulta protegida GET /anomalias/.
- Las rutas de registro, verificacion, login y recuperacion.

Solo se sustituyeron la generacion de codigos ficticios y el envio
de correos para evitar dependencias externas.

Se aprobaron 12 verificaciones, incluyendo:

- Registro y activacion de cuenta.
- Rechazo de cuenta sin verificar.
- Rechazo de acceso sin JWT.
- Acceso mediante JWT valido.
- Rechazo de JWT alterado.
- Recuperacion de contrasena.
- Rechazo de la contrasena anterior.
- Acceso con la nueva contrasena.
- Acceso protegido con un nuevo JWT.

Resultado: 12 verificaciones satisfactorias.

## 7. Aislamiento y proteccion de datos

Las pruebas utilizaron contenedores y bases de datos temporales.

Segun las verificaciones finales realizadas:

- Los contenedores temporales fueron eliminados.
- Las redes temporales fueron eliminadas.
- No se publicaron puertos de PostgreSQL temporal.
- No se utilizaron volumenes del PostgreSQL principal.
- La API y el PostgreSQL principales conservaron su estado.
- La rama main permanecio limpia.
- No se realizaron migraciones sobre el PostgreSQL principal
  como parte de estas pruebas.

Las contrasenas y correos utilizados en las pruebas de autenticacion
fueron ficticios.

## 8. GitHub Actions

En la revision previa del Pull Request 19 se comprobaron dos
verificaciones exitosas:

- Backend - isolated tests.
- Frontend - production build.

Estas verificaciones corresponden al Pull Request revisado en esa
fecha. No deben interpretarse como una ejecucion automatica de todas
las pruebas locales descritas en este documento.

## 9. Limitaciones y pendientes

Continuan pendientes:

- Verificacion de entrega de correos con SMTP real.
- Automatizacion de pruebas de navegador con una herramienta E2E.
- Pruebas de instalacion limpia en otros equipos o entornos.
- Pruebas integrales de carga y seguridad.
- Validacion funcional de servicios externos y credenciales reales.
- Incorporacion de las pruebas locales a GitHub Actions cuando
  resulte apropiado.

Las verificaciones realizadas no constituyen una certificacion de
seguridad ni garantizan el comportamiento en produccion.

## 10. Conclusion

La fase 12.48 aporto evidencia local favorable sobre instalacion
limpia, construccion de imagenes, integridad de archivos, navegacion
basica, registro, verificacion, inicio de sesion, recuperacion y
proteccion de rutas mediante JWT.

Los resultados permiten continuar con la preparacion de la entrega,
manteniendo identificadas las comprobaciones que todavia faltan.
