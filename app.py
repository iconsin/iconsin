import os
import json
import sys
import requests
from flask import Flask, request, jsonify

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================

ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "iconsin-bot"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)

# ============================================================
# FUNCIÓN PARA ENVIAR MENSAJES A WHATSAPP
# ============================================================

def send_whatsapp_message(to, text):
    """Envía un mensaje de texto a un número de WhatsApp usando la Cloud API."""
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
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")

# ============================================================
# WEBHOOK DE VERIFICACIÓN (GET)
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
# WEBHOOK PRINCIPAL (POST)
# ============================================================

@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    print("\n📬 === NUEVO EVENTO RECIBIDO ===")

    raw = request.get_data(as_text=True)
    print("🔹 Cuerpo RAW recibido:")
    print(raw if raw.strip() else "(vacío)")

    data = None
    try:
        data = request.get_json(force=True, silent=True)
        if not data and raw.strip():
            data = json.loads(raw)
        print("\n🔹 JSON decodificado:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Error al decodificar JSON: {e}")

    # Detectar tipo de evento (para saber si es message o status)
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        field = changes.get("field", "N/A")
        print(f"🔔 Tipo de evento recibido: {field}")

        messages = value.get("messages", [])
        if messages:
            msg = messages[0]
            from_number = msg.get("from")
            text = msg.get("text", {}).get("body", "")
            print(f"📩 MENSAJE DETECTADO de {from_number}: {text}")

            # Responder al usuario
            send_whatsapp_message(from_number, "✅ Mensaje recibido correctamente por el servidor Flask (Render).")
        else:
            print("ℹ️ No hay mensajes de texto en este evento.")
    except Exception as e:
        print(f"⚠️ No se pudo procesar el mensaje: {e}")

    return "EVENT_RECEIVED", 200

# ============================================================
# RUTA DE PRUEBA LOCAL
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "bot": "Chatbot IA Empresarial"}), 200

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Forzar logs en tiempo real en Render
    sys.stdout.reconfigure(line_buffering=True)

    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Iniciando Chatbot IA Empresarial en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
