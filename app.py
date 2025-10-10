# app.py (Diagnóstico nivel 2)
import os
import requests
from flask import Flask, request, jsonify

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)

def enviar_mensaje(destinatario, texto):
    """Envía mensaje a WhatsApp Cloud API."""
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": destinatario,
            "type": "text",
            "text": {"body": texto}
        }

        print(f"📤 Enviando mensaje a {destinatario}...")
        r = requests.post(WHATSAPP_URL, headers=headers, json=data)
        print(f"🔎 Código HTTP: {r.status_code}")
        print(f"🔎 Respuesta completa: {r.text}")

        if r.status_code != 200:
            print("⚠️ Falló el envío a WhatsApp.")

    except Exception as e:
        print("❌ Error en enviar_mensaje:", e)

@app.route("/whatsapp/webhook", methods=["POST"])
def recibir_mensaje():
    """Procesa mensajes recibidos desde Meta."""
    try:
        print("📥 Se recibió un POST en /whatsapp/webhook.")
        data = request.get_json(silent=True)
        print("🧾 JSON recibido crudo:", data)

        if not data:
            print("⚠️ No hay datos en el POST.")
            return "NO DATA", 200

        if data.get("object") != "whatsapp_business_account":
            print("⚠️ No es un mensaje de WhatsApp.")
            return "NOT WHATSAPP", 200

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    numero = msg.get("from")
                    texto = msg.get("text", {}).get("body", "")
                    print(f"📩 MENSAJE RECIBIDO: {texto} (de {numero})")

                    if numero and texto:
                        enviar_mensaje(numero, f"✅ Hola {numero}, tu mensaje fue recibido correctamente.")

        return "EVENT_RECEIVED", 200

    except Exception as e:
        print("❌ Error general en webhook:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/whatsapp/webhook", methods=["GET"])
def verificar_webhook():
    """Verificación inicial del Webhook."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente con Meta.")
        return challenge, 200
    else:
        print("❌ Falló la verificación del webhook.")
        return "Error de verificación", 403


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "diagnostic-v2"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Bot diagnóstico v2 en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

