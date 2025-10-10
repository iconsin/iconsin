# app.py
import os
import requests
from flask import Flask, request, jsonify
from gemini_handler import chat_answer

# ============================================================
# CONFIGURACIÓN
# ============================================================
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "TU_TOKEN_PERMANENTE_AQUI"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"
BUSINESS_NAME = "ICONSA"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ============================================================
# ENVÍO DE MENSAJES A WHATSAPP
# ============================================================
def send_whatsapp_message(to: str, text: str):
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
    try:
        r = requests.post(WHATSAPP_URL, headers=headers, json=payload)
        print(f"📤 Enviando a {to}: {text}")
        print(f"🔎 Respuesta Meta: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")

# ============================================================
# WEBHOOK - RECEPCIÓN DE MENSAJES
# ============================================================
@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    try:
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")

        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        messages = changes["value"].get("messages")

        if not messages:
            return "EVENT_RECEIVED", 200

        msg = messages[0]
        user_number = msg["from"]
        text = msg.get("text", {}).get("body", "").strip()

        print(f"💬 Mensaje recibido de {user_number}: {text}")

        # Procesar con Gemini
        if text:
            respuesta = chat_answer(text, business_name=BUSINESS_NAME)
        else:
            respuesta = "Hola 👋, soy el asistente virtual de ICONSA. ¿En qué puedo ayudarte?"

        print(f"🤖 Respuesta generada: {respuesta}")
        send_whatsapp_message(user_number, respuesta)

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
# RUTA PRINCIPAL
# ============================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "ICONSA WhatsApp Bot",
        "version": "2.0",
        "description": "Bot conectado a Meta Cloud API y Gemini"
    })

# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando bot en puerto {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
