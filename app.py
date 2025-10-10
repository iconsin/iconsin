# app.py
import os
import requests
from flask import Flask, request, jsonify
from gemini_handler import procesar_mensaje

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"  # tu número de WhatsApp Business
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ============================================================
# FUNCIÓN PARA ENVIAR MENSAJES
# ============================================================
def send_whatsapp_message(to, text):
    """
    Envía un mensaje de texto al número indicado.
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
        print(f"🔎 Respuesta Meta: {response.status_code} - {response.text}")

        if response.status_code != 200:
            print("⚠️ Error al enviar mensaje a WhatsApp")

    except Exception as e:
        print(f"❌ Error en send_whatsapp_message: {e}")

# ============================================================
# WEBHOOK POST (RECEPCIÓN DE MENSAJES)
# ============================================================
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📨 Payload recibido de Meta:\n", data)

        if data.get("object") == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])

                    for message in messages:
                        from_wa = message.get("from")
                        msg_type = message.get("type", "text")
                        text_body = ""

                        # Texto normal
                        if msg_type == "text":
                            text_body = (message.get("text", {}) or {}).get("body", "").strip()

                        # Botones o listas
                        elif msg_type == "interactive":
                            interactive = message.get("interactive", {})
                            text_body = (
                                (interactive.get("button_reply", {}) or {}).get("title")
                                or (interactive.get("list_reply", {}) or {}).get("title")
                                or ""
                            )
                        else:
                            text_body = ""

                        print(f"📩 Mensaje entrante desde {from_wa} (tipo: {msg_type})")
                        print(f"📝 Texto procesado: '{text_body}'")

                        if text_body:
                            respuesta = procesar_mensaje(text_body)
                            print(f"🤖 Respuesta automática: {respuesta}")
                            send_whatsapp_message(from_wa, respuesta)

        return "EVENT_RECEIVED", 200
    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "ERROR", 500

# ============================================================
# WEBHOOK GET (VERIFICACIÓN)
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
# SERVIDOR LOCAL
# ============================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "ICONSA WhatsApp Bot"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando ICONSA WhatsApp Bot en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
