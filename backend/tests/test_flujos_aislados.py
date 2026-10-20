
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch


class PruebasFlujosAislados(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert
        from fastapi.testclient import TestClient
        import dotenv

        if "app.main" in sys.modules:
            raise RuntimeError(
                "La aplicacion fue importada antes del aislamiento."
            )

        cls.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        cls.Session = sessionmaker(
            bind=cls.engine,
            autoflush=False,
            autocommit=False
        )

        variables = {
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "SECRET_KEY": "t" * 64,
            "GROQ_API_KEY": "test-key-no-real",
            "SENDER_EMAIL": "noreply@example.invalid",
            "SENDER_PASSWORD": "test-no-real",
        }

        with patch.dict(os.environ, variables):
            with patch.object(
                dotenv, "load_dotenv",
                return_value=False
            ):
                from app import database

                database.engine = cls.engine
                database.SessionLocal = cls.Session

                from app import schema_migrations

                with patch.object(
                    schema_migrations,
                    "migrate_legacy_auth_schema",
                    return_value=None
                ):
                    from app import main

        if main.engine is not cls.engine:
            raise RuntimeError(
                "El backend no utiliza el motor aislado."
            )

        if (
            main.engine.url.get_backend_name()
            != "sqlite"
        ):
            raise RuntimeError(
                "Motor de pruebas no permitido."
            )

        main.SessionLocal = cls.Session
        main.pg_insert = sqlite_insert

        cls.main = main
        cls.models = main.models

        cls.parche_correo = patch.object(
            main,
            "enviar_correo_verificacion",
            return_value=None
        )
        cls.parche_codigo = patch.object(
            main,
            "generar_codigo_seguro",
            return_value="135791"
        )

        cls.parche_correo.start()
        cls.parche_codigo.start()

        # No se usa el context manager de TestClient.
        # Por ello no se ejecuta el startup del simulador.
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "client"):
            cls.client.close()
        if hasattr(cls, "parche_correo"):
            cls.parche_correo.stop()
        if hasattr(cls, "parche_codigo"):
            cls.parche_codigo.stop()
        if hasattr(cls, "engine"):
            cls.engine.dispose()

    def setUp(self):
        # Todas estas operaciones se limitan a SQLite
        # en memoria; nunca al PostgreSQL de PluriOne.
        if self.main.engine is not self.engine:
            raise RuntimeError(
                "Se perdio el aislamiento de la BD."
            )

        self.models.Base.metadata.drop_all(self.engine)
        self.models.Base.metadata.create_all(self.engine)

    def registrar(self, correo):
        respuesta = self.client.post(
            "/registro/",
            json={
                "nombre_completo": "Usuario de prueba",
                "correo": correo,
                "telefono": None,
                "password": "ClaveSegura123!"
            }
        )
        self.assertEqual(
            respuesta.status_code, 200,
            respuesta.text
        )
        return respuesta

    def verificar(self, correo, codigo="135791"):
        return self.client.post(
            "/verificar/",
            json={
                "correo": correo,
                "codigo": codigo
            }
        )

    def activar(self, correo):
        self.registrar(correo)
        respuesta = self.verificar(correo)
        self.assertEqual(
            respuesta.status_code, 200,
            respuesta.text
        )

    def token(self, correo, password="ClaveSegura123!"):
        respuesta = self.client.post(
            "/login/",
            data={
                "username": correo,
                "password": password
            }
        )
        self.assertEqual(
            respuesta.status_code, 200,
            respuesta.text
        )
        return respuesta.json()["access_token"]

    def usuario(self, correo):
        with self.Session() as db:
            usuario = db.query(
                self.models.User
            ).filter_by(correo=correo).first()

            self.assertIsNotNone(usuario)

            return {
                "id": usuario.id,
                "activo": usuario.is_active,
                "codigo": usuario.codigo_verificacion,
                "intentos": usuario.codigo_intentos
            }

    def test_01_codigo_correcto_y_login(self):
        correo = "correcto@example.invalid"

        self.registrar(correo)
        antes = self.usuario(correo)

        self.assertFalse(antes["activo"])

        respuesta = self.verificar(correo)
        self.assertEqual(respuesta.status_code, 200)

        despues = self.usuario(correo)
        self.assertTrue(despues["activo"])
        self.assertIsNone(despues["codigo"])

        self.assertTrue(self.token(correo))

    def test_02_codigo_incorrecto(self):
        correo = "incorrecto@example.invalid"

        self.registrar(correo)

        respuesta = self.verificar(
            correo, "000000"
        )

        self.assertEqual(respuesta.status_code, 400)

        estado = self.usuario(correo)
        self.assertFalse(estado["activo"])
        self.assertEqual(estado["intentos"], 1)

    def test_03_codigo_vencido(self):
        correo = "vencido@example.invalid"
        self.registrar(correo)

        with self.Session() as db:
            usuario = db.query(
                self.models.User
            ).filter_by(correo=correo).one()

            usuario.codigo_expira_en = (
                datetime.utcnow()
                - timedelta(seconds=30)
            )
            db.commit()

        respuesta = self.verificar(correo)

        self.assertEqual(respuesta.status_code, 400)

        estado = self.usuario(correo)
        self.assertFalse(estado["activo"])
        self.assertIsNone(estado["codigo"])

    def test_04_quinto_intento_bloqueado(self):
        correo = "bloqueado@example.invalid"
        self.registrar(correo)

        for numero in range(5):
            respuesta = self.verificar(
                correo, "000000"
            )
            self.assertEqual(
                respuesta.status_code, 400,
                "Intento " + str(numero + 1)
            )

        estado = self.usuario(correo)

        self.assertEqual(estado["intentos"], 5)
        self.assertIsNone(estado["codigo"])

        respuesta = self.verificar(
            correo, "135791"
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_05_recuperacion_de_password(self):
        correo = "recuperar@example.invalid"
        self.activar(correo)

        solicitud = self.client.post(
            "/solicitar-recuperacion/",
            json={"correo": correo}
        )

        self.assertEqual(solicitud.status_code, 200)

        respuesta = self.client.post(
            "/recuperar-password/",
            json={
                "correo": correo,
                "codigo": "135791",
                "nueva_password": "NuevaClave123!"
            }
        )

        self.assertEqual(
            respuesta.status_code, 200,
            respuesta.text
        )

        token = self.token(
            correo, "NuevaClave123!"
        )

        self.assertTrue(token)

        estado = self.usuario(correo)
        self.assertIsNone(estado["codigo"])

    def test_06_recuperacion_no_revela_cuentas(self):
        correo = "existente@example.invalid"
        self.activar(correo)

        existente = self.client.post(
            "/solicitar-recuperacion/",
            json={"correo": correo}
        )

        inexistente = self.client.post(
            "/solicitar-recuperacion/",
            json={
                "correo": "ausente@example.invalid"
            }
        )

        self.assertEqual(existente.status_code, 200)
        self.assertEqual(inexistente.status_code, 200)
        self.assertEqual(
            existente.json(),
            inexistente.json()
        )

    def test_07_aislamiento_archivado_restauracion(self):
        correo_a = "usuarioa@example.invalid"
        correo_b = "usuariob@example.invalid"

        self.activar(correo_a)
        self.activar(correo_b)

        token_a = self.token(correo_a)
        token_b = self.token(correo_b)

        id_a = self.usuario(correo_a)["id"]
        id_b = self.usuario(correo_b)["id"]

        with self.Session() as db:
            for uid, nombre in (
                (id_a, "Pipeline A"),
                (id_b, "Pipeline B")
            ):
                db.add(self.models.AnomalyLog(
                    user_id=uid,
                    pipeline_name=nombre,
                    metric_type="latencia",
                    value=200.0,
                    status="Alerta",
                    ai_recommendation="Prueba aislada",
                    archived=False
                ))

            db.commit()

        headers_a = {
            "Authorization": "Bearer " + token_a
        }

        headers_b = {
            "Authorization": "Bearer " + token_b
        }

        consulta_a = self.client.get(
            "/anomalias/", headers=headers_a
        )

        self.assertEqual(consulta_a.status_code, 200)
        self.assertEqual(len(consulta_a.json()), 1)
        self.assertEqual(
            consulta_a.json()[0]["pipeline_name"],
            "Pipeline A"
        )

        archivado = self.client.delete(
            "/anomalias/", headers=headers_a
        )

        self.assertEqual(
            archivado.status_code, 200,
            archivado.text
        )

        consulta_b = self.client.get(
            "/anomalias/", headers=headers_b
        )

        self.assertEqual(consulta_b.status_code, 200)
        self.assertEqual(len(consulta_b.json()), 1)

        consulta_a = self.client.get(
            "/anomalias/", headers=headers_a
        )

        self.assertEqual(consulta_a.json(), [])

        restauracion = self.client.post(
            "/anomalias/restaurar/",
            headers=headers_a
        )

        self.assertEqual(
            restauracion.status_code, 200,
            restauracion.text
        )

        consulta_a = self.client.get(
            "/anomalias/", headers=headers_a
        )

        self.assertEqual(len(consulta_a.json()), 1)

        with self.Session() as db:
            total = db.query(
                self.models.AnomalyLog
            ).count()
            self.assertEqual(total, 2)

    def test_08_login_limite_429(self):
        respuestas = []

        for _ in range(16):
            respuesta = self.client.post(
                "/login/",
                data={
                    "username": "ausente@example.invalid",
                    "password": "PasswordIncorrecta123!"
                }
            )
            respuestas.append(respuesta)

        for respuesta in respuestas[:15]:
            self.assertEqual(
                respuesta.status_code, 401,
                respuesta.text
            )

        self.assertEqual(
            respuestas[15].status_code, 429
        )

        self.assertIn(
            "retry-after",
            respuestas[15].headers
        )



    def test_09_ingesta_sin_token(self):
        respuesta = self.client.post(
            "/metricas/",
            json={
                "pipeline": "Pipeline Seguro",
                "metrica": "latencia_ms",
                "valor": 500
            }
        )

        self.assertEqual(respuesta.status_code, 401)

        with self.Session() as db:
            self.assertEqual(
                db.query(self.models.AnomalyLog).count(), 0
            )

    def test_10_ingesta_autenticada_y_websocket(self):
        from unittest.mock import AsyncMock
        import json

        correo = "ingesta@example.invalid"
        self.activar(correo)

        token = self.token(correo)
        uid = self.usuario(correo)["id"]

        with patch.object(
            self.main.manager,
            "send_to_user",
            new_callable=AsyncMock
        ) as enviar:

            respuesta = self.client.post(
                "/metricas/",
                headers={
                    "Authorization": "Bearer " + token
                },
                json={
                    "pipeline": "Pipeline Medicion",
                    "metrica": "latencia_ms",
                    "valor": 500
                }
            )

            self.assertEqual(
                respuesta.status_code, 201,
                respuesta.text
            )

            self.assertEqual(
                respuesta.json()["status"],
                "Alerta"
            )

            self.assertTrue(
                respuesta.json()["registrada"]
            )

            enviar.assert_awaited_once()

            uid_destino, mensaje = enviar.await_args.args

            self.assertEqual(uid_destino, uid)

            evento = json.loads(mensaje)

            self.assertEqual(
                evento["pipeline_name"],
                "Pipeline Medicion"
            )

        with self.Session() as db:
            registros = db.query(
                self.models.AnomalyLog
            ).all()

            self.assertEqual(len(registros), 1)
            self.assertEqual(registros[0].user_id, uid)
            self.assertFalse(registros[0].archived)

    def test_11_ingesta_valores_invalidos(self):
        correo = "validacion@example.invalid"
        self.activar(correo)

        token = self.token(correo)

        casos = [
            {
                "pipeline": "Pipeline Test",
                "metrica": "latencia_ms",
                "valor": -1
            },
            {
                "pipeline": "Pipeline Test",
                "metrica": "datos_corruptos_%",
                "valor": 101
            },
            {
                "pipeline": "Pipeline Test",
                "metrica": "metrica_desconocida",
                "valor": 50
            },
            {
                "pipeline": "",
                "metrica": "latencia_ms",
                "valor": 50
            },
        ]

        for caso in casos:
            respuesta = self.client.post(
                "/metricas/",
                headers={
                    "Authorization": "Bearer " + token
                },
                json=caso
            )

            self.assertEqual(
                respuesta.status_code, 422,
                respuesta.text
            )

        with self.Session() as db:
            self.assertEqual(
                db.query(self.models.AnomalyLog).count(),
                0
            )

    def test_12_ingesta_aislada_dos_usuarios(self):
        correo_a = "fuentea@example.invalid"
        correo_b = "fuenteb@example.invalid"

        self.activar(correo_a)
        self.activar(correo_b)

        token_a = self.token(correo_a)
        token_b = self.token(correo_b)

        for token, nombre in (
            (token_a, "Origen A"),
            (token_b, "Origen B"),
        ):
            respuesta = self.client.post(
                "/metricas/",
                headers={
                    "Authorization": "Bearer " + token
                },
                json={
                    "pipeline": nombre,
                    "metrica": "tasa_fallos_%",
                    "valor": 20
                }
            )

            self.assertEqual(
                respuesta.status_code, 201,
                respuesta.text
            )

        for token, esperado in (
            (token_a, "Origen A"),
            (token_b, "Origen B"),
        ):
            respuesta = self.client.get(
                "/anomalias/",
                headers={
                    "Authorization": "Bearer " + token
                }
            )

            self.assertEqual(
                respuesta.status_code, 200
            )

            self.assertEqual(
                len(respuesta.json()), 1
            )

            self.assertEqual(
                respuesta.json()[0]["pipeline_name"],
                esperado
            )

        with self.Session() as db:
            self.assertEqual(
                db.query(self.models.AnomalyLog).count(),
                2
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
