# app.py
import os
import requests
from flask import Flask, request, jsonify
from gemini_handler import chat_answer

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN
# ==========================================
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"
BUSINESS_NAME = "ICONSA"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ==========================================
# FUNCIÓN: ENVIAR MENSAJE
# ==========================================
def send_whatsapp_message(to, text):
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
        r = requests.post(WHATSAPP_URL, headers=headers, json=payload)
        print(f"📤 Enviado a {to}: {text}")
        print(f"🔎 Respuesta Meta: {r.status_code} - {r.text}")
        if r.status_code != 200:
            print("⚠️ Error al enviar mensaje a WhatsApp")
    except Exception as e:
        print(f"❌ Error en send_whatsapp_message: {e}")

# ==========================================
# WEBHOOK PRINCIPAL (POST)
# ==========================================
@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    try:
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")

        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            print("📭 Evento sin mensajes (status update)")
            return "EVENT_RECEIVED", 200

        msg = messages[0]
        user_number = msg.get("from")
        text_body = msg.get("text", {}).get("body", "").strip()

        if not text_body:
            print("🕳 Mensaje vacío o no de texto.")
            return "EVENT_RECEIVED", 200

        print(f"💬 Mensaje recibido de {user_number}: {text_body}")

        # Procesar con Gemini
        try:
            respuesta = chat_answer(text_body, business_name=BUSINESS_NAME)
        except Exception as e:
            print(f"⚠️ Error IA: {e}")
            respuesta = "Hola 👋, soy el asistente de ICONSA. ¿En qué puedo ayudarte?"

        send_whatsapp_message(user_number, respuesta)
        return "EVENT_RECEIVED", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# VERIFICACIÓN DEL WEBHOOK (GET)
# ==========================================
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

# ==========================================
# RUTA RAÍZ
# ==========================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "ICONSA WhatsApp Bot",
        "version": "1.1"
    })

# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando ICONSA WhatsApp Bot en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
