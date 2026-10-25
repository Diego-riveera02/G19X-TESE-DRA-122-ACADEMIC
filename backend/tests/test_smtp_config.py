import pytest

from app import email_utils


@pytest.mark.parametrize(
    "tls,auth,esperado",
    [
        (None, None, ["conexion", "tls", "auth", "envio", "salida"]),
        ("false", "false", ["conexion", "envio", "salida"]),
        ("valor_invalido", "valor_invalido", ["conexion", "tls", "auth", "envio", "salida"]),
    ],
)
def test_configuracion_smtp(monkeypatch, tls, auth, esperado):
    eventos = []

    class SMTPFalso:
        def __init__(self, servidor, puerto):
            assert servidor == "mailpit"
            assert puerto == 1025
            eventos.append("conexion")

        def starttls(self):
            eventos.append("tls")

        def login(self, usuario, password):
            eventos.append("auth")

        def send_message(self, mensaje):
            eventos.append("envio")

        def quit(self):
            eventos.append("salida")

    monkeypatch.setattr(email_utils.smtplib, "SMTP", SMTPFalso)

    for variable, valor in (("SMTP_STARTTLS", tls), ("SMTP_AUTH", auth)):
        if valor is None:
            monkeypatch.delenv(variable, raising=False)
        else:
            monkeypatch.setenv(variable, valor)

    email_utils._enviar_correo_verificacion_impl(
        "destinatario@example.invalid",
        "123456",
        smtp_server="mailpit",
        smtp_port=1025,
        sender_email="remitente@example.invalid",
        sender_password="credencial_ficticia",
    )

    assert eventos == esperado
