# Validación de Mailpit — Corte 5

## 1. Objetivo

Comprobar el registro, verificación y acceso a PluriOne utilizando correo SMTP local mediante Mailpit, sin depender de Gmail.

## 2. Entorno de pruebas

- Fecha: 27 de octubre de 2026.
- Commit base: `dae0942`.
- PostgreSQL: puerto local 5433.
- FastAPI: puerto local 8000.
- React: puerto local 5173.
- Mailpit: puerto local 8025.
- SMTP interno: `mailpit:1025`.
- Perfil Docker Compose: `correo-local`.

## 3. Configuración SMTP utilizada

- `SMTP_SERVER=mailpit`
- `SMTP_PORT=1025`
- `SMTP_STARTTLS=false`
- `SMTP_AUTH=false`
- `SENDER_EMAIL=no-responder@plurione.local`
- `SENDER_PASSWORD=`

La configuración privada original fue respaldada fuera del repositorio. No se publican credenciales.

## 4. Prueba funcional

Cuenta ficticia: `prueba.corte5.001@example.test`.

1. Se envió el formulario de registro desde React.
2. La plataforma mostró la pantalla de verificación.
3. Mailpit recibió el correo de verificación.
4. Se obtuvo un código de seis dígitos.
5. PluriOne aceptó el código y activó la cuenta.
6. El usuario inició sesión correctamente.
7. Se visualizó el dashboard principal.

**Resultado: prueba funcional satisfactoria.**

## 5. Verificaciones técnicas

- PostgreSQL y Mailpit alcanzaron el estado healthy.
- FastAPI respondió HTTP 200.
- React respondió HTTP 200.
- Se comprobaron las seis variables SMTP del contenedor API.
- Docker Compose reconoció los servicios con y sin el perfil opcional.
- Se restauró `backend/.env` desde el respaldo privado y se verificó su integridad mediante SHA-256.
- Se recreó FastAPI con la configuración original y respondió HTTP 200.
- Se confirmó que FastAPI ya no conserva las cuatro variables SMTP temporales de Mailpit.
- Se detuvo Mailpit correctamente, con estado `Exited (0)`.
- El arranque normal mantuvo PostgreSQL, FastAPI y React funcionando sin Mailpit.
- PostgreSQL permaneció `healthy` y FastAPI y React respondieron HTTP 200.

La comprobación del arranque normal reutilizó contenedores existentes. No equivale a una instalación literal desde un clon nuevo.

## 6. Evidencia visual

Se observaron capturas del registro, correo recibido, formulario de verificación, activación exitosa y dashboard autenticado.

Las capturas fueron revisadas durante la sesión. Todavía no se incorporaron al repositorio. Antes de publicarlas deben ocultarse los códigos de verificación y otros datos sensibles.

## 7. Pendientes

- [x] Configuración privada original restaurada y verificada con SHA-256.
- [x] Arranque normal comprobado con tres servicios y Mailpit detenido.
- [ ] Obtener la revisión de los bots del Corte 5 e incorporar capturas sanitizadas al repositorio si se solicitan.

## 8. Conclusión

Se comprobó que PluriOne permite registrar, verificar y autenticar un usuario mediante Mailpit sin utilizar un buzón real de Gmail.
