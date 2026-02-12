from flask import Flask, request
import requests, imaplib, email, re, os

app = Flask(__name__)

# Variables de entorno
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
DESTINATION_NUMBER = os.environ.get("DESTINATION_NUMBER")

# Función enviar WhatsApp
def send_whatsapp_message(msg):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": DESTINATION_NUMBER,
        "type": "text",
        "text": {"body": msg}
    }
    requests.post(url, headers=headers, json=payload)

# Verificación webhook
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge
    return "Error", 403

# Recibir mensajes de WhatsApp
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

        if message.lower() == "codigo":
            code = get_latest_code()
            if code:
                send_whatsapp_message(f"Tu código es: {code}")
            else:
                send_whatsapp_message("No encontré ningún código reciente.")

    except:
        pass

    return "ok", 200


# Función leer último código del email
def get_latest_code():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        result, data = mail.search(None, "UNSEEN")

        for mail_id in reversed(data[0].split()):
            result, msg_data = mail.fetch(mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            match = re.search(r"\b\d{6}\b", body)

            if match:
                return match.group()

        mail.logout()

    except Exception as e:
        print(e)

    return None


# iniciar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

