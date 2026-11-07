"""Prueba aislada del chat sin llave de Groq."""

import os
import unittest
from unittest.mock import patch

# Use isolated in-memory SQLite while importing the router.
with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:'}):
    from app.chat_router import ChatRequest, crear_router_chat


class PruebasChatSinLlave(unittest.TestCase):
    def test_chat_informa_configuracion_faltante(self):
        router = crear_router_chat(
            get_current_user=lambda: object(),
            limitar_chat_por_usuario=lambda: None,
            client=None,
        )

        rutas = [
            ruta for ruta in router.routes
            if getattr(ruta, "path", None) == "/chat/"
        ]

        self.assertEqual(len(rutas), 1)

        solicitud = ChatRequest(
            anomaly_id=0,
            pregunta="Explica esta anomalia",
            contexto_anomalia="",
            historial=[],
        )

        respuesta = rutas[0].endpoint(
            solicitud,
            current_user=object(),
            db=object(),
            _limite_chat=None,
        )

        self.assertIsInstance(respuesta, dict)
        self.assertIn("GROQ_API_KEY", respuesta["respuesta"])
        self.assertIn("backend/.env", respuesta["respuesta"])
        self.assertIn("reinicia la API", respuesta["respuesta"])
        self.assertNotIn(
            "Intenta nuevamente",
            respuesta["respuesta"],
        )


if __name__ == "__main__":
    unittest.main()
