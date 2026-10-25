# Evidencia funcional E2E - Cuarto corte

## 1. Identificacion

- Proyecto: Plataforma de Observabilidad de Datos con Inteligencia Artificial.
- Empresa: PluriOne S.A. de C.V.
- Responsable: Diego Rivera Aguilar.
- Fecha: 25 de octubre de 2026.
- Commit evaluado: f738d13.
- Resultado: prueba principal de ingesta satisfactoria.

## 2. Objetivo

Comprobar la integracion real entre React, FastAPI y PostgreSQL.
El flujo evaluado comprende autenticacion, creacion de pipelines,
envio de metricas externas y visualizacion de anomalias.

## 3. Entorno aislado

- Proyecto Docker: plurione_e2e_1252.
- PostgreSQL: servicio db con volumen independiente.
- FastAPI: http://127.0.0.1:8001.
- React: http://127.0.0.1:5173.
- Frontend configurado con VITE_API_URL al puerto 8001.

Las pruebas se realizaron en un clon independiente.
El proyecto original no se modifico durante la ejecucion.

## 4. Procedimiento y resultados

1. Se verifico la disponibilidad de los servicios.
2. Se inicio sesion desde React con un usuario ficticio.
3. Se creo el pipeline plurione-e2e-corte4-1252.
4. Se obtuvo una clave API para el pipeline.
5. Se envio una metrica a POST /metricas/externas/.
6. Se utilizo el encabezado X-Pipeline-Key.

Metrica enviada:

- metrica: latencia_ms
- valor: 9500

Respuesta de la API: HTTP 201.

Anomalias antes de la solicitud: 27.
Anomalias despues de la solicitud: 28.

El dashboard mostro una alerta critica correspondiente
al pipeline de prueba y a la metrica latencia_ms = 9500.

## 5. Resultado

La prueba confirmo el flujo de ingesta externa,
registro de una nueva anomalia y visualizacion en React.

## 6. Seguridad y aislamiento

- No se publico ninguna clave API.
- No se utilizaron credenciales SMTP reales.
- No se modifico la base de datos original.
- No se eliminaron volumenes.
- No se modifico codigo fuente para esta evidencia.

## 7. Limitaciones

La cuenta de prueba fue activada directamente en la base
de datos aislada debido a la ausencia de SMTP de prueba.

Esta evidencia no demuestra el proceso completo de
verificacion por correo, el funcionamiento de Groq,
ni todas las pruebas de seguridad del sistema.

## 8. Conclusion

Se verifico satisfactoriamente la integracion principal
React - FastAPI - PostgreSQL mediante una metrica real
enviada al endpoint de ingesta externa.
