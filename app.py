import os
import re
from flask import Flask, request
import requests
import pyotp

app = Flask(__name__)

# =============================
# CONFIGURACIÓN
# =============================

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# 🔐 TU NÚMERO AUTORIZADO (Chile)
AUTHORIZED_NUMBERS = [
    "56955148723"
]

# 🔒 PIN DE SEGURIDAD
BOT_PIN = os.getenv("BOT_PIN")  # Ejemplo en Render: 8342

# =============================
# EMAILS PERMITIDOS + SECRETOS TOTP
# =============================

TOTP_SECRETS = {
    "juanito23@gmail.com": "BASE32SECRET123",
    "robertito23@gmail.com": "BASE32SECRET456"
}

# =============================
# FUNCIONES
# =============================

def is_authorized(number):
    return number in AUTHORIZED_NUMBERS

def generate_totp(email):
    secret = TOTP_SECRETS.get(email)
    if not secret:
        return None
    totp = pyotp.TOTP(secret)
    return totp.now()

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

# =============================
# VERIFICACIÓN WEBHOOK META
# =============================

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error de verificación"

# =============================
# RECEPCIÓN DE MENSAJES
# =============================

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender_number = message["from"]
        text = message["text"]["body"].strip()

        # 🔐 Validar número autorizado
        if not is_authorized(sender_number):
            send_whatsapp_message(sender_number, "⛔ No estás autorizado para usar este bot.")
            return "ok"

        # 📨 Si pide código
        if text.lower().startswith("quiero el codigo de"):
            send_whatsapp_message(sender_number, "🔐 Ingresa tu PIN de seguridad:")
            app.config[sender_number] = text
            return "ok"

        # 🔒 Validación de PIN
        if sender_number in app.config:
            if text == BOT_PIN:
                original_request = app.config.pop(sender_number)
                email_match = re.search(r"[\w\.-]+@[\w\.-]+", original_request)

                if email_match:
                    email = email_match.group()
                    code = generate_totp(email)

                    if code:
                        send_whatsapp_message(sender_number, f"✅ Código para {email}:\n\n{code}")
                    else:
                        send_whatsapp_message(sender_number, "❌ Ese correo no está autorizado.")
                else:
                    send_whatsapp_message(sender_number, "❌ No se detectó un correo válido.")
            else:
                send_whatsapp_message(sender_number, "❌ PIN incorrecto.")
            return "ok"

        # 📌 Mensaje por defecto
        send_whatsapp_message(sender_number, "Escribe:\nQuiero el codigo de correo@gmail.com")

    except Exception as e:
        print("Error:", e)

    return "ok"

# =============================
# INICIO SERVIDOR
# =============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


