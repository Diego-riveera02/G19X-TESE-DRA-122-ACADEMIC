import unittest
import urllib.request
import urllib.error


BASE = "http://127.0.0.1:8000"

OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({})
)


def solicitar(ruta, metodo, token=None):
    headers = {}

    if token is not None:
        headers["Authorization"] = (
            "Bearer " + token
        )

    peticion = urllib.request.Request(
        BASE + ruta,
        headers=headers,
        method=metodo
    )

    try:
        with OPENER.open(
            peticion, timeout=15
        ) as respuesta:
            return respuesta.status

    except urllib.error.HTTPError as error:
        return error.code


class PruebasSeguridadArchivado(unittest.TestCase):

    def test_01_consulta_sin_token(self):
        self.assertEqual(
            solicitar("/anomalias/", "GET"),
            401
        )

    def test_02_consulta_token_invalido(self):
        self.assertEqual(
            solicitar(
                "/anomalias/", "GET",
                "invalid.jwt.token"
            ),
            401
        )

    def test_03_archivadas_sin_token(self):
        self.assertEqual(
            solicitar(
                "/anomalias/archivadas/", "GET"
            ),
            401
        )

    def test_04_archivadas_token_invalido(self):
        self.assertEqual(
            solicitar(
                "/anomalias/archivadas/",
                "GET",
                "invalid.jwt.token"
            ),
            401
        )

    def test_05_archivar_sin_token(self):
        self.assertEqual(
            solicitar("/anomalias/", "DELETE"),
            401
        )

    def test_06_archivar_token_invalido(self):
        self.assertEqual(
            solicitar(
                "/anomalias/", "DELETE",
                "invalid.jwt.token"
            ),
            401
        )

    def test_07_restaurar_sin_token(self):
        self.assertEqual(
            solicitar(
                "/anomalias/restaurar/", "POST"
            ),
            401
        )

    def test_08_restaurar_token_invalido(self):
        self.assertEqual(
            solicitar(
                "/anomalias/restaurar/",
                "POST",
                "invalid.jwt.token"
            ),
            401
        )


if __name__ == "__main__":
    unittest.main()
