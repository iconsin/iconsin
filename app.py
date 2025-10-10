# app.py
import os
import requests
from flask import Flask, request, jsonify
from gemini_handler import chat_answer

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "TU_TOKEN_PERMANENTE_AQUI"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "25681420111462727"  # ID de tu número de WhatsApp
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "ICONSA")

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ============================================================
# FUNCIÓN PARA ENVIAR MENSAJES A WHATSAPP
# ============================================================
def send_whatsapp_message(to: str, text: str):
    """
    Envía un mensaje de texto a un número de WhatsApp usando la Cloud API.
    """
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }

        response = requests.post(WHATSAPP_URL, headers=headers, json=payload)
        print(f"📤 Enviado a {to}: {text}")
        print(f"🔎 Respuesta de Meta: {response.status_code} - {response.text}")

        if response.status_code != 200:
            print("⚠️ Error al enviar el mensaje a WhatsApp.")
    except Exception as e:
        print(f"❌ Error en send_whatsapp_message: {e}")

# ============================================================
# WEBHOOK PARA RECIBIR MENSAJES (POST)
# ============================================================
@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    try:
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")

        # A veces Meta envía notificaciones de "status", no "messages"
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        # Si no hay mensajes (ej: status, ack, etc.)
        if not messages:
            print("⚙️ Evento no contiene mensajes (probablemente status update).")
            return "EVENT_RECEIVED", 200

        # Extraer datos del mensaje
        message = messages[0]
        from_wa = message.get("from")
        msg_type = message.get("type", "")
        text_body = ""

        # Soporte para tipos de mensaje: text, interactive, etc.
        if msg_type == "text":
            text_body = message["text"].get("body", "")
        elif msg_type == "interactive":
            interactive = message.get("interactive", {})
            text_body = (
                (interactive.get("button_reply", {}) or {}).get("title") or
                (interactive.get("list_reply", {}) or {}).get("title") or ""
            )
        else:
            print(f"⚠️ Tipo de mensaje no soportado: {msg_type}")
            return "EVENT_RECEIVED", 200

        # Procesar con Gemini
        if text_body:
            print(f"🤖 Mensaje recibido de {from_wa}: {text_body}")
            ai_response = chat_answer(text_body, business_name=BUSINESS_NAME)
            print(f"🧠 Respuesta IA: {ai_response}")

            send_whatsapp_message(to=from_wa, text=ai_response)

        return "EVENT_RECEIVED", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================
# VERIFICACIÓN DEL WEBHOOK (GET)
# ============================================================
@app.route("/whatsapp/webhook", methods=["GET"])
def verify_token():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge, 200
    else:
        print("❌ Error de verificación del webhook.")
        return "Error de verificación", 403


# ============================================================
# SERVIDOR LOCAL O DEPLOY
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor WhatsApp+Gemini en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
