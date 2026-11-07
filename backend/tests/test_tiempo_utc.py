"""Pruebas aisladas del contrato UTC de PluriOne."""

import ast
import calendar
import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from app.tiempo import ahora_utc


APP = Path(__file__).resolve().parents[1] / "app"


class PruebasTiempoUTC(unittest.TestCase):

    def test_01_devuelve_datetime_sin_zona(self):
        resultado = ahora_utc()

        self.assertIsInstance(resultado, datetime)
        self.assertIsNone(resultado.tzinfo)

    def test_02_corresponde_al_reloj_utc(self):
        antes = datetime.now(timezone.utc).replace(tzinfo=None)
        resultado = ahora_utc()
        despues = datetime.now(timezone.utc).replace(tzinfo=None)

        margen = timedelta(seconds=1)

        self.assertGreaterEqual(resultado, antes - margen)
        self.assertLessEqual(resultado, despues + margen)

    def test_03_utiliza_timezone_utc(self):
        fijo = datetime(
            2026, 11, 3, 18, 30, 15,
            tzinfo=timezone.utc,
        )

        with patch("app.tiempo.datetime") as reloj:
            reloj.now.return_value = fijo
            resultado = ahora_utc()
            reloj.now.assert_called_once_with(timezone.utc)

        self.assertEqual(
            resultado,
            datetime(2026, 11, 3, 18, 30, 15),
        )
        self.assertIsNone(resultado.tzinfo)

    def test_04_modelos_conservan_defaults_callable(self):
        texto = (APP / "models.py").read_text(encoding="utf-8")
        arbol = ast.parse(texto)

        defaults = []

        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Call):
                for argumento in nodo.keywords:
                    if argumento.arg == "default":
                        valor = argumento.value

                        if (
                            isinstance(valor, ast.Name)
                            and valor.id == "ahora_utc"
                        ):
                            defaults.append(valor)

        self.assertEqual(len(defaults), 3)
        self.assertIn("DateTime(timezone=True)", texto)
        self.assertNotIn("default=ahora_utc()", texto)

    def test_05_sin_datetime_utcnow_en_app(self):
        restantes = []

        for archivo in APP.rglob("*.py"):
            texto = archivo.read_text(encoding="utf-8")

            if "datetime.utcnow" in texto:
                restantes.append(archivo.name)

        self.assertEqual(restantes, [])

    def test_06_auth_router_usa_helper_compartido(self):
        texto = (APP / "auth_router.py").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "from .tiempo import ahora_utc",
            texto,
        )
        self.assertGreaterEqual(texto.count("ahora_utc()"), 6)
        self.assertNotIn(
            "datetime.now(timezone.utc)",
            texto,
        )

    def test_07_jwt_expiracion_explicita(self):
        if importlib.util.find_spec("jose") is None:
            self.skipTest("python-jose no instalado localmente")

        from jose import jwt
        from app.jwt_utils import encode_access_token

        fijo = datetime(2026, 11, 3, 18, 30, 0)
        duracion = timedelta(minutes=7)

        with patch(
            "app.jwt_utils.ahora_utc",
            return_value=fijo,
        ):
            token = encode_access_token(
                {"sub": "test@example.invalid"},
                expires_delta=duracion,
                secret_key="clave-de-pruebas-utc",
                algorithm="HS256",
            )

        contenido = jwt.get_unverified_claims(token)

        esperado = calendar.timegm(
            (fijo + duracion).utctimetuple()
        )

        self.assertEqual(contenido["exp"], esperado)
        self.assertEqual(
            contenido["sub"],
            "test@example.invalid",
        )

    def test_08_jwt_expiracion_predeterminada(self):
        if importlib.util.find_spec("jose") is None:
            self.skipTest("python-jose no instalado localmente")

        from jose import jwt
        from app.jwt_utils import encode_access_token

        fijo = datetime(2026, 11, 3, 18, 30, 0)

        with patch(
            "app.jwt_utils.ahora_utc",
            return_value=fijo,
        ):
            token = encode_access_token(
                {"sub": "test@example.invalid"},
                secret_key="clave-de-pruebas-utc",
                algorithm="HS256",
            )

        contenido = jwt.get_unverified_claims(token)

        esperado = calendar.timegm(
            (fijo + timedelta(minutes=15)).utctimetuple()
        )

        self.assertEqual(contenido["exp"], esperado)


if __name__ == "__main__":
    unittest.main()
