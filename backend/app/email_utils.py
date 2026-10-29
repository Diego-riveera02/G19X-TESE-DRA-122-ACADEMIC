"""Funciones auxiliares de correo SMTP."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _enviar_correo_verificacion_impl(destinatario, codigo, *, smtp_server, smtp_port, sender_email, sender_password, proposito="verificacion"):
    if proposito not in ("verificacion", "recuperacion"):
        raise ValueError("Proposito de correo no valido")

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinatario
        msg['Subject'] = (
            '🔒 Código de Verificación - PluriOne'
            if proposito == "verificacion"
            else '🔑 Código de Recuperación - PluriOne'
        )
        body = f'\n        <html>\n            <body style="font-family: Arial, sans-serif; background-color: #0b0c10; color: #c5c6c7; padding: 20px;">\n                <div style="border: 2px solid #E5B80B; border-radius: 8px; padding: 30px; background-color: #1a1a1d; text-align: center;">\n                    <h2 style="color: #E5B80B; margin-top: 0;">VERIFICACIÓN DE CUENTA PLURIONE</h2>\n                    <p style="font-size: 16px;">Para completar tu solicitud, ingresa el siguiente código de 6 dígitos en la plataforma:</p>\n                    <div style="background-color: #0b0c10; padding: 15px; margin: 20px 0; border-radius: 8px; display: inline-block;">\n                        <h1 style="color: #E63946; margin: 0; letter-spacing: 5px;">{codigo}</h1>\n                    </div>\n                    <p style="font-size: 12px; color: #888;">Si tú no solicitaste este acceso, puedes ignorar este mensaje.</p>\n                </div>\n            </body>\n        </html>\n        '
        if proposito == "recuperacion":
            body = body.replace(
                "VERIFICACIÓN DE CUENTA PLURIONE",
                "RECUPERACIÓN DE CONTRASEÑA PLURIONE",
            ).replace(
                "Para completar tu solicitud, ingresa el siguiente código de 6 dígitos en la plataforma:",
                "Para restablecer tu contraseña, introduce este código de 6 dígitos en PluriOne:",
            )

        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(smtp_server, smtp_port)
        if os.getenv("SMTP_STARTTLS", "true").strip().lower() != "false":
            server.starttls()
        if os.getenv("SMTP_AUTH", "true").strip().lower() != "false":
            server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f'Error al enviar código de verificación: {e}')
