# Bot de WhatsApp 2FA

Este proyecto envía automáticamente los códigos 2FA de tu correo a tu WhatsApp usando WhatsApp Cloud API y un servidor en Render.

## Archivos

- `app.py` → código del bot
- `requirements.txt` → librerías necesarias
- `README.md` → documentación (este archivo)

## Variables de entorno necesarias

| Nombre             | Descripción |
|-------------------|-------------|
| VERIFY_TOKEN       | Token para verificar webhook de Meta |
| ACCESS_TOKEN       | Access Token de WhatsApp Cloud API |
| PHONE_NUMBER_ID    | ID de tu número de WhatsApp |
| EMAIL_USER         | Tu correo Gmail |
| EMAIL_PASS         | App Password de Gmail |
| DESTINATION_NUMBER | Tu número WhatsApp (ej: 5491123456789) |

## Cómo funciona

1. El bot revisa tu correo cada minuto.
2. Detecta códigos de 6 dígitos (2FA).
3. Envía automáticamente el código a tu WhatsApp.
