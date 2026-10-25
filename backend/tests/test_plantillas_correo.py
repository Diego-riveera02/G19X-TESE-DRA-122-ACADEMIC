"""Pruebas aisladas de los correos de PluriOne."""

import unittest

from email.header import decode_header, make_header
from unittest.mock import patch

from app import email_utils


class PruebasPlantillasCorreo(unittest.TestCase):

    def enviar_simulado(self, proposito=None):
        opciones = {
            "smtp_server": "smtp.example.invalid",
            "smtp_port": 587,
            "sender_email": "remitente@example.invalid",
            "sender_password": "credencial-ficticia",
        }

        if proposito is not None:
            opciones["proposito"] = proposito

        with patch.object(email_utils.smtplib, "SMTP") as smtp:
            email_utils._enviar_correo_verificacion_impl(
                "destinatario@example.invalid",
                "123456",
                **opciones
            )

            smtp.assert_called_once_with(
                "smtp.example.invalid",
                587
            )

            servidor = smtp.return_value

            servidor.starttls.assert_called_once()
            servidor.login.assert_called_once()
            servidor.send_message.assert_called_once()

            mensaje = servidor.send_message.call_args.args[0]

        asunto = str(
            make_header(decode_header(str(mensaje["Subject"])))
        )

        cuerpo = (
            mensaje.get_payload()[0]
            .get_payload(decode=True)
            .decode("utf-8")
        )

        self.assertIn("123456", cuerpo)

        return asunto, cuerpo

    def test_01_verificacion_por_defecto(self):
        asunto, cuerpo = self.enviar_simulado()

        self.assertIn(
            "C\u00f3digo de Verificaci\u00f3n",
            asunto
        )

        self.assertIn(
            "VERIFICACI\u00d3N DE CUENTA PLURIONE",
            cuerpo
        )

        self.assertNotIn(
            "RECUPERACI\u00d3N DE CONTRASE\u00d1A PLURIONE",
            cuerpo
        )

    def test_02_recuperacion(self):
        asunto, cuerpo = self.enviar_simulado("recuperacion")

        self.assertIn(
            "C\u00f3digo de Recuperaci\u00f3n",
            asunto
        )

        self.assertIn(
            "RECUPERACI\u00d3N DE CONTRASE\u00d1A PLURIONE",
            cuerpo
        )

        self.assertNotIn(
            "VERIFICACI\u00d3N DE CUENTA PLURIONE",
            cuerpo
        )

    def test_03_asuntos_diferentes(self):
        asunto_v, _ = self.enviar_simulado("verificacion")
        asunto_r, _ = self.enviar_simulado("recuperacion")

        self.assertNotEqual(asunto_v, asunto_r)

    def test_04_proposito_invalido(self):
        with patch.object(email_utils.smtplib, "SMTP") as smtp:
            with self.assertRaises(ValueError):
                email_utils._enviar_correo_verificacion_impl(
                    "destinatario@example.invalid",
                    "123456",
                    smtp_server="smtp.example.invalid",
                    smtp_port=587,
                    sender_email="remitente@example.invalid",
                    sender_password="credencial-ficticia",
                    proposito="desconocido"
                )

            smtp.assert_not_called()


if __name__ == "__main__":
    unittest.main()
