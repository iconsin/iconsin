import os
import json
import requests
from flask import Flask, request, jsonify

# ============================================================
# CONFIGURACIÓN
# ============================================================
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)

# ============================================================
# FUNCIÓN PARA ENVIAR MENSAJES
# ============================================================
def send_whatsapp_message(to, text):
    """Envía un mensaje simple de texto a WhatsApp Cloud API."""
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
    print("\n=================== 📬 NUEVO EVENTO RECIBIDO ===================")

    raw = request.get_data(as_text=True)
    if not raw.strip():
        print("⚠️ Advertencia: cuerpo vacío recibido.")
        return "EVENT_RECEIVED", 200

    print("🔹 RAW BODY:\n", raw)
    try:
        data = json.loads(raw)
    except Exception as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return "Bad Request", 400

    # Registrar todo el JSON por claridad
    print("🔍 JSON decodificado:\n", json.dumps(data, indent=2))

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        # Si no hay mensajes (ejemplo: solo "statuses")
        if not messages:
            print("ℹ️ No se encontraron mensajes (posible evento de status o plantilla).")
            return "EVENT_RECEIVED", 200

        msg = messages[0]
        from_number = msg.get("from")
        msg_type = msg.get("type")
        msg_text = ""

        if msg_type == "text":
            msg_text = msg.get("text", {}).get("body", "")
        elif msg_type == "interactive":
            msg_text = msg.get("interactive", {}).get("button_reply", {}).get("title", "")
        else:
            msg_text = f"(mensaje tipo {msg_type})"

        print(f"📩 MENSAJE DETECTADO de {from_number}: {msg_text}")

        # Responder
        send_whatsapp_message(from_number, "✅ Mensaje recibido correctamente por el servidor Flask (Render).")

    except Exception as e:
        print(f"⚠️ Error procesando mensaje: {e}")

    print("===============================================================\n")
    return "EVENT_RECEIVED", 200

# ============================================================
# RUTA DE PRUEBA LOCAL
# ============================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "WhatsApp Diagnostic Bot"}), 200

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Iniciando bot de diagnóstico en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)


