import json
import os
import subprocess
import unittest
import urllib.error
import urllib.request


API = "http://127.0.0.1:8000"
FRONTEND = "http://127.0.0.1:5173"


def solicitar(url, metodo="GET", cuerpo=None, headers=None):
    datos = None

    if cuerpo is not None:
        datos = json.dumps(cuerpo).encode("utf-8")

    solicitud = urllib.request.Request(
        url,
        data=datos,
        method=metodo,
        headers=headers or {},
    )

    try:
        with urllib.request.urlopen(solicitud, timeout=15) as r:
            return r.status, r.read(), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers


class PruebasIntegracionPluriOne(unittest.TestCase):

    def test_01_fastapi(self):
        codigo, _, _ = solicitar(API + "/docs")
        self.assertEqual(codigo, 200)

    def test_02_react(self):
        codigo, _, _ = solicitar(FRONTEND + "/")
        self.assertEqual(codigo, 200)

    def test_03_rutas_principales(self):
        codigo, contenido, _ = solicitar(API + "/openapi.json")
        self.assertEqual(codigo, 200)

        rutas = json.loads(contenido)["paths"]

        necesarias = {
            "/registro/",
            "/verificar/",
            "/reenviar-verificacion/",
            "/login/",
            "/solicitar-recuperacion/",
            "/recuperar-password/",
            "/chat/",
            "/anomalias/",
        }

        self.assertTrue(necesarias.issubset(rutas.keys()))

    def test_04_anomalias_sin_token(self):
        codigo, _, _ = solicitar(API + "/anomalias/")
        self.assertEqual(codigo, 401)

    def test_05_anomalias_token_invalido(self):
        codigo, _, _ = solicitar(
            API + "/anomalias/",
            headers={"Authorization": "Bearer token_invalido"},
        )
        self.assertEqual(codigo, 401)

    def test_06_chat_sin_token(self):
        cuerpo = {
            "anomaly_id": 0,
            "pregunta": "Prueba de seguridad",
            "contexto_anomalia": "",
            "historial": [],
        }

        codigo, _, _ = solicitar(
            API + "/chat/",
            metodo="POST",
            cuerpo=cuerpo,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(codigo, 401)

    def test_07_chat_token_invalido(self):
        cuerpo = {
            "anomaly_id": 0,
            "pregunta": "Prueba de seguridad",
            "contexto_anomalia": "",
            "historial": [],
        }

        codigo, _, _ = solicitar(
            API + "/chat/",
            metodo="POST",
            cuerpo=cuerpo,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token_invalido",
            },
        )
        self.assertEqual(codigo, 401)

    def test_08_cors(self):
        origen = "http://localhost:5173"

        codigo, _, headers = solicitar(
            API + "/chat/",
            metodo="OPTIONS",
            headers={
                "Origin": origen,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers":
                    "authorization,content-type",
            },
        )

        self.assertEqual(codigo, 200)
        self.assertEqual(
            headers.get("Access-Control-Allow-Origin"),
            origen,
        )

    def test_09_postgresql_y_modelos(self):
        codigo_python = (
            "from sqlalchemy import inspect, text; "
            "from app.database import engine; "
            "from app import models; "
            "c=engine.connect(); "
            "assert c.execute(text('SELECT 1')).scalar()==1; "
            "i=inspect(c); "
            "assert {'users','anomaly_logs','auth_rate_limits'}"
            ".issubset(set(i.get_table_names())); "
            "columnas={x['name'] for x in i.get_columns('users')}; "
            "assert {'codigo_expira_en','codigo_intentos',"
            "'codigo_proposito'}.issubset(columnas); "
            "c.close(); print('POSTGRESQL OK')"
        )

        resultado = subprocess.run(
            [
                "docker", "compose", "exec", "-T",
                "api", "python", "-c", codigo_python,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(
            resultado.returncode,
            0,
            resultado.stderr,
        )
        self.assertIn("POSTGRESQL OK", resultado.stdout)


    @unittest.skipUnless(
        os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("COMPOSE_PROJECT_NAME")
        == "plurione_http_ci",
        "Solo en GitHub Actions con Docker aislado",
    )
    def test_10_registro_limite_y_activacion_mailpit(self):
        import re
        import time
        import uuid

        mailpit = "http://127.0.0.1:8025"
        correo = f"ci-auth-{uuid.uuid4().hex}@example.invalid"

        claves = [
            "ClaveTemporal01!",
            "ClaveTemporal02!",
            "ClaveTemporal03!",
        ]

        def enviar_json(ruta, cuerpo):
            return solicitar(
                API + ruta,
                metodo="POST",
                cuerpo=cuerpo,
                headers={"Content-Type": "application/json"},
            )

        # Tres registros del mismo correo deben permitirse.
        for indice, clave in enumerate(claves, start=1):
            codigo_http, contenido, _ = enviar_json(
                "/registro/",
                {
                    "nombre_completo": "Usuario CI aislado",
                    "correo": correo,
                    "telefono": None,
                    "password": clave,
                },
            )

            self.assertEqual(
                codigo_http,
                200,
                f"Registro {indice}: {contenido!r}",
            )

        # La cuarta solicitud excede el limite por correo.
        codigo_http, contenido, encabezados = enviar_json(
            "/registro/",
            {
                "nombre_completo": "Intento excedido CI",
                "correo": correo,
                "telefono": None,
                "password": "ClaveTemporal04!",
            },
        )

        self.assertEqual(
            codigo_http,
            429,
            contenido.decode("utf-8", errors="replace"),
        )

        reintentar = encabezados.get("Retry-After")

        self.assertIsNotNone(reintentar)
        self.assertGreater(int(reintentar), 0)

        # Confirmar que Mailpit recibio los tres correos.
        mensajes = []

        for _ in range(40):
            estado, cuerpo, _ = solicitar(
                mailpit + "/api/v1/messages?limit=100"
            )

            self.assertEqual(estado, 200)

            bandeja = json.loads(cuerpo.decode("utf-8"))

            mensajes = [
                mensaje
                for mensaje in bandeja.get("messages", [])
                if correo in [
                    destino.get("Address", "").lower()
                    for destino in mensaje.get("To", [])
                    if isinstance(destino, dict)
                ]
            ]

            if len(mensajes) >= 3:
                break

            time.sleep(0.25)

        self.assertEqual(
            len(mensajes),
            3,
            "Mailpit no recibio exactamente tres correos.",
        )

        # Recuperar el codigo del ultimo registro.
        ultimo = max(
            mensajes,
            key=lambda mensaje: mensaje.get("Created", ""),
        )

        identificador = ultimo.get("ID")
        self.assertTrue(identificador)

        estado, cuerpo, _ = solicitar(
            mailpit + "/api/v1/message/" + identificador
        )

        self.assertEqual(estado, 200)

        mensaje = json.loads(cuerpo.decode("utf-8"))
        html = mensaje.get("HTML", "")

        encontrado = re.search(
            r"<h1\b[^>]*>\s*([0-9]{6})\s*</h1>",
            html,
            flags=re.IGNORECASE,
        )

        self.assertIsNotNone(
            encontrado,
            "No se encontro el codigo en el correo de Mailpit.",
        )

        codigo_correo = encontrado.group(1)

        # Sin password no se debe activar.
        estado, _, _ = enviar_json(
            "/verificar/",
            {
                "correo": correo,
                "codigo": codigo_correo,
            },
        )

        self.assertEqual(estado, 422)

        # La clave del primer registro ya no debe servir.
        estado, _, _ = enviar_json(
            "/verificar/",
            {
                "correo": correo,
                "codigo": codigo_correo,
                "password": claves[0],
            },
        )

        self.assertEqual(estado, 400)

        # El codigo y la ultima clave deben activar.
        estado, contenido, _ = enviar_json(
            "/verificar/",
            {
                "correo": correo,
                "codigo": codigo_correo,
                "password": claves[-1],
            },
        )

        self.assertEqual(
            estado,
            200,
            contenido.decode("utf-8", errors="replace"),
        )

if __name__ == "__main__":
    unittest.main()
