
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



    def test_13_websocket_rechaza_token_invalido(self):
        from starlette.websockets import WebSocketDisconnect

        with self.client.websocket_connect(
            "/ws/anomalias",
            headers={"origin": "http://localhost:5173"}
        ) as ws:
            ws.send_json({
                "type": "auth",
                "token": "token-invalido"
            })

            with self.assertRaises(
                WebSocketDisconnect
            ) as resultado:
                ws.receive_json()

            self.assertEqual(
                resultado.exception.code, 1008
            )

    def test_14_websocket_rechaza_origen(self):
        from starlette.websockets import WebSocketDisconnect

        with self.assertRaises(
            WebSocketDisconnect
        ) as resultado:
            with self.client.websocket_connect(
                "/ws/anomalias",
                headers={
                    "origin": "https://origen-no-autorizado.invalid"
                }
            ) as ws:
                ws.send_json({
                    "type": "auth",
                    "token": "invalido"
                })

        self.assertEqual(
            resultado.exception.code, 1008
        )

    def test_15_websocket_autenticacion_correcta(self):
        correo = "websocket@example.invalid"
        self.activar(correo)

        token = self.token(correo)
        usuario_id = self.usuario(correo)["id"]

        with self.client.websocket_connect(
            "/ws/anomalias",
            headers={"origin": "http://localhost:5173"}
        ) as ws:
            ws.send_json({
                "type": "auth",
                "token": token
            })

            self.assertEqual(
                ws.receive_json(),
                {"type": "auth_ok"}
            )

            self.assertIn(
                usuario_id,
                self.main.manager.active_connections
            )

        self.assertNotIn(
            usuario_id,
            self.main.manager.active_connections
        )

    def test_16_websocket_aislamiento_dos_usuarios(self):
        correo_a = "websocketa@example.invalid"
        correo_b = "websocketb@example.invalid"

        self.activar(correo_a)
        self.activar(correo_b)

        token_a = self.token(correo_a)
        token_b = self.token(correo_b)

        id_a = self.usuario(correo_a)["id"]
        id_b = self.usuario(correo_b)["id"]

        self.assertNotEqual(id_a, id_b)

        with self.client.websocket_connect(
            "/ws/anomalias",
            headers={"origin": "http://localhost:5173"}
        ) as ws_a:

            ws_a.send_json({
                "type": "auth",
                "token": token_a
            })

            self.assertEqual(
                ws_a.receive_json(),
                {"type": "auth_ok"}
            )

            with self.client.websocket_connect(
                "/ws/anomalias",
                headers={
                    "origin": "http://localhost:5173"
                }
            ) as ws_b:

                ws_b.send_json({
                    "type": "auth",
                    "token": token_b
                })

                self.assertEqual(
                    ws_b.receive_json(),
                    {"type": "auth_ok"}
                )

                self.assertIn(
                    id_a,
                    self.main.manager.active_connections
                )

                self.assertIn(
                    id_b,
                    self.main.manager.active_connections
                )

                for token, nombre in (
                    (token_a, "Evento exclusivo A"),
                    (token_b, "Evento exclusivo B"),
                ):
                    respuesta = self.client.post(
                        "/metricas/",
                        headers={
                            "Authorization": "Bearer " + token
                        },
                        json={
                            "pipeline": nombre,
                            "metrica": "latencia_ms",
                            "valor": 500
                        }
                    )

                    self.assertEqual(
                        respuesta.status_code,
                        201,
                        respuesta.text
                    )

                evento_a = ws_a.receive_json()
                evento_b = ws_b.receive_json()

                self.assertEqual(
                    evento_a["pipeline_name"],
                    "Evento exclusivo A"
                )

                self.assertEqual(
                    evento_b["pipeline_name"],
                    "Evento exclusivo B"
                )

                self.assertNotEqual(
                    evento_a["id"],
                    evento_b["id"]
                )

        with self.Session() as db:
            registros = db.query(
                self.models.AnomalyLog
            ).all()

            self.assertEqual(len(registros), 2)
            self.assertEqual(
                {r.user_id for r in registros},
                {id_a, id_b}
            )



    def test_17_pipeline_clave_hasheada_y_listado(self):
        import hashlib

        correo = "pipeline17@example.invalid"
        self.activar(correo)
        token = self.token(correo)

        respuesta = self.client.post(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token},
            json={"nombre": "Fuente Ventas"}
        )

        self.assertEqual(
            respuesta.status_code, 201, respuesta.text
        )

        datos = respuesta.json()
        clave = datos["clave_api"]

        self.assertTrue(clave.startswith("plr_"))
        self.assertGreater(len(clave), 35)

        with self.Session() as db:
            p = db.query(self.models.Pipeline).one()
            self.assertEqual(p.nombre, "Fuente Ventas")
            self.assertNotEqual(p.clave_hash, clave)
            self.assertEqual(
                p.clave_hash,
                hashlib.sha256(
                    clave.encode("utf-8")
                ).hexdigest()
            )

        listado = self.client.get(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token}
        )

        self.assertEqual(listado.status_code, 200)
        self.assertEqual(len(listado.json()), 1)
        self.assertNotIn("clave_api", str(listado.json()))
        self.assertNotIn("clave_hash", str(listado.json()))

    def test_18_pipeline_sin_jwt_y_duplicado(self):
        datos = {"nombre": "Pipeline Duplicado"}

        sin_token = self.client.post(
            "/pipelines/", json=datos
        )
        self.assertEqual(sin_token.status_code, 401)

        correo = "pipeline18@example.invalid"
        self.activar(correo)
        token = self.token(correo)
        headers = {"Authorization": "Bearer " + token}

        primera = self.client.post(
            "/pipelines/", headers=headers, json=datos
        )
        segunda = self.client.post(
            "/pipelines/", headers=headers, json=datos
        )

        self.assertEqual(primera.status_code, 201)
        self.assertEqual(segunda.status_code, 409)

        with self.Session() as db:
            self.assertEqual(
                db.query(self.models.Pipeline).count(), 1
            )

    def test_19_ingesta_externa_con_clave(self):
        correo = "pipeline19@example.invalid"
        self.activar(correo)
        token = self.token(correo)

        creado = self.client.post(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token},
            json={"nombre": "Fuente Externa"}
        )
        self.assertEqual(creado.status_code, 201)
        clave = creado.json()["clave_api"]

        cuerpo = {
            "metrica": "latencia_ms",
            "valor": 500
        }

        sin_clave = self.client.post(
            "/metricas/externas/", json=cuerpo
        )
        self.assertEqual(sin_clave.status_code, 401)

        invalida = self.client.post(
            "/metricas/externas/",
            headers={"X-Pipeline-Key": "clave-invalida"},
            json=cuerpo
        )
        self.assertEqual(invalida.status_code, 401)

        valido = self.client.post(
            "/metricas/externas/",
            headers={"X-Pipeline-Key": clave},
            json=cuerpo
        )
        self.assertEqual(
            valido.status_code, 201, valido.text
        )
        self.assertEqual(
            valido.json()["pipeline_name"],
            "Fuente Externa"
        )
        self.assertEqual(
            valido.json()["status"], "Alerta"
        )

        porcentaje_invalido = self.client.post(
            "/metricas/externas/",
            headers={"X-Pipeline-Key": clave},
            json={
                "metrica": "tasa_fallos_%",
                "valor": 101
            }
        )
        self.assertEqual(
            porcentaje_invalido.status_code, 422
        )

        with self.Session() as db:
            registros = db.query(
                self.models.AnomalyLog
            ).all()
            self.assertEqual(len(registros), 1)

    def test_20_pipelines_aislamiento_usuarios(self):
        from unittest.mock import AsyncMock

        correo_a = "pipeline20a@example.invalid"
        correo_b = "pipeline20b@example.invalid"

        self.activar(correo_a)
        self.activar(correo_b)

        token_a = self.token(correo_a)
        token_b = self.token(correo_b)
        id_b = self.usuario(correo_b)["id"]

        a = self.client.post(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token_a},
            json={"nombre": "Fuente de A"}
        )
        b = self.client.post(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token_b},
            json={"nombre": "Fuente de B"}
        )

        self.assertEqual(a.status_code, 201)
        self.assertEqual(b.status_code, 201)

        ajeno = self.client.post(
            "/pipelines/" + str(a.json()["id"]) + "/rotar/",
            headers={"Authorization": "Bearer " + token_b}
        )
        self.assertEqual(ajeno.status_code, 404)

        listado_b = self.client.get(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token_b}
        )
        self.assertEqual(listado_b.status_code, 200)
        self.assertEqual(len(listado_b.json()), 1)
        self.assertEqual(
            listado_b.json()[0]["nombre"],
            "Fuente de B"
        )

        with patch.object(
            self.main.manager,
            "send_to_user",
            new_callable=AsyncMock
        ) as enviar:
            respuesta = self.client.post(
                "/metricas/externas/",
                headers={
                    "X-Pipeline-Key": b.json()["clave_api"]
                },
                json={
                    "metrica": "latencia_ms",
                    "valor": 600
                }
            )

            self.assertEqual(
                respuesta.status_code, 201, respuesta.text
            )
            enviar.assert_awaited_once()
            self.assertEqual(
                enviar.await_args.args[0], id_b
            )

        consulta_a = self.client.get(
            "/anomalias/",
            headers={"Authorization": "Bearer " + token_a}
        )
        consulta_b = self.client.get(
            "/anomalias/",
            headers={"Authorization": "Bearer " + token_b}
        )

        self.assertEqual(consulta_a.json(), [])
        self.assertEqual(len(consulta_b.json()), 1)

    def test_21_rotacion_invalida_clave_anterior(self):
        correo = "pipeline21@example.invalid"
        self.activar(correo)
        token = self.token(correo)

        creado = self.client.post(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token},
            json={"nombre": "Fuente Rotacion"}
        )

        self.assertEqual(creado.status_code, 201)

        antiguo = creado.json()["clave_api"]
        identificador = creado.json()["id"]

        rotado = self.client.post(
            "/pipelines/" + str(identificador) + "/rotar/",
            headers={"Authorization": "Bearer " + token}
        )

        self.assertEqual(rotado.status_code, 200)
        nuevo = rotado.json()["clave_api"]
        self.assertNotEqual(antiguo, nuevo)

        cuerpo = {
            "metrica": "latencia_ms",
            "valor": 700
        }

        anterior = self.client.post(
            "/metricas/externas/",
            headers={"X-Pipeline-Key": antiguo},
            json=cuerpo
        )
        vigente = self.client.post(
            "/metricas/externas/",
            headers={"X-Pipeline-Key": nuevo},
            json=cuerpo
        )

        self.assertEqual(anterior.status_code, 401)
        self.assertEqual(vigente.status_code, 201)

    def test_22_revocacion_invalida_pipeline(self):
        correo = "pipeline22@example.invalid"
        self.activar(correo)
        token = self.token(correo)

        creado = self.client.post(
            "/pipelines/",
            headers={"Authorization": "Bearer " + token},
            json={"nombre": "Fuente Revocada"}
        )

        self.assertEqual(creado.status_code, 201)
        clave = creado.json()["clave_api"]
        identificador = creado.json()["id"]

        revocado = self.client.post(
            "/pipelines/" + str(identificador) + "/revocar/",
            headers={"Authorization": "Bearer " + token}
        )
        self.assertEqual(revocado.status_code, 200)
        self.assertTrue(revocado.json()["revocado"])

        denegado = self.client.post(
            "/metricas/externas/",
            headers={"X-Pipeline-Key": clave},
            json={
                "metrica": "latencia_ms",
                "valor": 800
            }
        )
        self.assertEqual(denegado.status_code, 401)

        rotacion = self.client.post(
            "/pipelines/" + str(identificador) + "/rotar/",
            headers={"Authorization": "Bearer " + token}
        )
        self.assertEqual(rotacion.status_code, 404)

        with self.Session() as db:
            self.assertEqual(
                db.query(self.models.AnomalyLog).count(),
                0
            )
            pipeline = db.query(
                self.models.Pipeline
            ).one()
            self.assertTrue(pipeline.revocado)



    def test_23_normal_temporal_sin_guardar(self):
        import asyncio
        import json
        from unittest.mock import AsyncMock

        correo = "simulador23@example.invalid"
        self.activar(correo)
        uid = self.usuario(correo)["id"]

        enviar = AsyncMock()

        with self.Session() as db:
            resultado = asyncio.run(
                self.main.registrar_metrica(
                    db=db,
                    user_id=uid,
                    pipeline="Pipeline Normal",
                    metrica="latencia_ms",
                    valor=100,
                    enviar_ws=enviar,
                    guardar_normales=False,
                )
            )

            self.assertEqual(
                db.query(self.models.AnomalyLog).count(),
                0
            )

        self.assertEqual(resultado["status"], "Normal")
        self.assertFalse(resultado["registrada"])
        self.assertIsNone(resultado["id"])
        self.assertTrue(resultado["timestamp"])

        enviar.assert_awaited_once()

        receptor, mensaje = enviar.await_args.args
        self.assertEqual(receptor, uid)

        evento = json.loads(mensaje)
        self.assertEqual(
            evento["type"], "metrica_normal"
        )
        self.assertFalse(evento["registrada"])

    def test_24_critica_se_guarda_y_notifica(self):
        import asyncio
        import json
        from unittest.mock import AsyncMock

        correo = "simulador24@example.invalid"
        self.activar(correo)
        uid = self.usuario(correo)["id"]

        enviar = AsyncMock()

        with self.Session() as db:
            resultado = asyncio.run(
                self.main.registrar_metrica(
                    db=db,
                    user_id=uid,
                    pipeline="Pipeline Critico",
                    metrica="latencia_ms",
                    valor=800,
                    enviar_ws=enviar,
                    recomendacion="Revisar servicio",
                    guardar_normales=False,
                )
            )

            registros = db.query(
                self.models.AnomalyLog
            ).all()

            self.assertEqual(len(registros), 1)
            self.assertEqual(registros[0].user_id, uid)
            self.assertEqual(
                registros[0].status, "Critico"
            )
            self.assertEqual(
                registros[0].ai_recommendation,
                "Revisar servicio"
            )

        self.assertTrue(resultado["registrada"])
        self.assertIsInstance(resultado["id"], int)

        enviar.assert_awaited_once()
        receptor, mensaje = enviar.await_args.args

        self.assertEqual(receptor, uid)
        evento = json.loads(mensaje)
        self.assertEqual(evento["status"], "Critico")

    def test_25_simulador_normal_no_llama_ia(self):
        import asyncio
        import json
        from unittest.mock import AsyncMock, Mock

        from app import metricas_service

        correo = "simulador25@example.invalid"
        self.activar(correo)
        uid = self.usuario(correo)["id"]

        enviar = AsyncMock()
        ia = Mock(return_value="No deberia utilizarse")

        with patch.object(
            metricas_service.random,
            "choice",
            side_effect=[
                "Pipeline Ventas MX",
                ("latencia_ms", 50.0, 900.0, "ms"),
            ],
        ):
            with patch.object(
                metricas_service.random,
                "uniform",
                return_value=100.0
            ):
                with self.Session() as db:
                    resultado = asyncio.run(
                        metricas_service.simular_metrica_usuario(
                            db=db,
                            user_id=uid,
                            enviar_ws=enviar,
                            generar_recomendacion=ia,
                        )
                    )

                    self.assertEqual(
                        db.query(
                            self.models.AnomalyLog
                        ).count(),
                        0
                    )

        ia.assert_not_called()
        enviar.assert_awaited_once()

        self.assertFalse(resultado["registrada"])
        self.assertEqual(resultado["status"], "Normal")

        evento = json.loads(
            enviar.await_args.args[1]
        )

        self.assertEqual(
            evento["type"], "metrica_normal"
        )
        self.assertEqual(
            enviar.await_args.args[0], uid
        )

    def test_26_simulador_alerta_usa_ia(self):
        import asyncio
        import json
        from unittest.mock import AsyncMock, Mock

        from app import metricas_service

        correo = "simulador26@example.invalid"
        self.activar(correo)
        uid = self.usuario(correo)["id"]

        enviar = AsyncMock()
        ia = Mock(return_value="Revisar latencia")

        with patch.object(
            metricas_service.random,
            "choice",
            side_effect=[
                "Pipeline Ventas MX",
                ("latencia_ms", 50.0, 900.0, "ms"),
            ],
        ):
            with patch.object(
                metricas_service.random,
                "uniform",
                return_value=500.0
            ):
                with self.Session() as db:
                    resultado = asyncio.run(
                        metricas_service.simular_metrica_usuario(
                            db=db,
                            user_id=uid,
                            enviar_ws=enviar,
                            generar_recomendacion=ia,
                        )
                    )

                    registros = db.query(
                        self.models.AnomalyLog
                    ).all()

                    self.assertEqual(len(registros), 1)
                    self.assertEqual(
                        registros[0].status,
                        "Alerta"
                    )
                    self.assertEqual(
                        registros[0].user_id, uid
                    )

        ia.assert_called_once_with(
            "Pipeline Ventas MX",
            "latencia_ms",
            500.0
        )

        self.assertTrue(resultado["registrada"])
        self.assertEqual(resultado["status"], "Alerta")

        enviar.assert_awaited_once()

        evento = json.loads(
            enviar.await_args.args[1]
        )

        self.assertEqual(
            evento["ai_recommendation"],
            "Revisar latencia"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
