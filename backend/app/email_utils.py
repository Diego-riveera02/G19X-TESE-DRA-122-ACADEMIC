"""Funciones auxiliares de correo SMTP."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .color_utils import get_color


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
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f'Error al enviar código de verificación: {e}')


def _enviar_alerta_correo_consolidado_impl(destinatario, lat_v, lat_s, cal_v, cal_s, fal_v, fal_s, diag_general, *, smtp_server, smtp_port, sender_email, sender_password):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinatario
        msg['Subject'] = '🚨 REPORTE CONSOLIDADO DE INFRAESTRUCTURA - PluriOne'
        body = f'\n        <html>\n            <body style="font-family: Arial, sans-serif; background-color: #0b0c10; color: #c5c6c7; padding: 20px;">\n                <div style="border: 2px solid #8B0000; border-radius: 8px; padding: 20px; background-color: #1a1a1d;">\n                    <h2 style="color: #E63946; margin-top: 0;">SISTEMA CENTRAL PLURIONE - REPORTE DE ESTADO</h2>\n                    <p>Se ha registrado un evento crítico. A continuación se presenta el estado consolidado de los tres componentes del sistema:</p>\n\n                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #111217;">\n                        <tr style="background-color: #333; color: #fff;">\n                            <th style="padding: 10px; text-align: left;">Componente / Métrica</th>\n                            <th style="padding: 10px; text-align: left;">Valor</th>\n                            <th style="padding: 10px; text-align: left;">Estado</th>\n                        </tr>\n                        <tr>\n                            <td style="padding: 10px; border-bottom: 1px solid #333;">Latencia de Red (API Gateway)</td>\n                            <td style="padding: 10px; border-bottom: 1px solid #333;">{lat_v}</td>\n                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(lat_s)};">{lat_s}</td>\n                        </tr>\n                        <tr>\n                            <td style="padding: 10px; border-bottom: 1px solid #333;">Calidad de Datos (Ventas MX)</td>\n                            <td style="padding: 10px; border-bottom: 1px solid #333;">{cal_v}</td>\n                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(cal_s)};">{cal_s}</td>\n                        </tr>\n                        <tr>\n                            <td style="padding: 10px; border-bottom: 1px solid #333;">Tasa de Fallos (Migración AWS)</td>\n                            <td style="padding: 10px; border-bottom: 1px solid #333;">{fal_v}</td>\n                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(fal_s)};">{fal_s}</td>\n                        </tr>\n                    </table>\n\n                    <h4 style="color: #E5B80B; margin-top: 25px; margin-bottom: 5px;">DIAGNÓSTICO DE CAUSA RAÍZ (J.A.R.V.I.S.)</h4>\n                    <div style="background-color: rgba(212, 160, 23, 0.1); border-left: 3px solid #E5B80B; padding: 12px; color: #e0e0e0; line-height: 1.5;">\n                        {diag_general}\n                    </div>\n                </div>\n            </body>\n        </html>\n        '
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f'Error al enviar correo: {e}')
