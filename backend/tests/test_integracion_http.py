import json
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


if __name__ == "__main__":
    unittest.main()
