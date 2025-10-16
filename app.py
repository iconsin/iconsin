import os
import json
import sys
from flask import Flask, request, jsonify
from meta_whatsapp import send_whatsapp_message
from gemini_handler import ask_gemini
from questionnaire import buscar_respuesta

# ==============================
# Configuración general
# ==============================
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = Flask(__name__)

# ==============================
# Ruta raíz de diagnóstico
# ==============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "bot": "Chatbot IA Empresarial"}), 200


# ==============================
# Verificación del webhook
# ==============================
@app.route("/whatsapp/webhook", methods=["GET"])
def verify_token():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge, 200
    return "Error de verificación", 403


# ==============================
# Recepción de mensajes WhatsApp
# ==============================
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    print("\n📬 === NUEVO EVENTO RECIBIDO ===")

    data = request.get_json(silent=True)
    print(json.dumps(data, indent=2))

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            from_number = msg.get("from")
            text = msg.get("text", {}).get("body", "").strip()

            print(f"📩 MENSAJE DETECTADO de {from_number}: {text}")

            # 1️⃣ Buscar respuesta en el cuestionario interno
            respuesta = buscar_respuesta(text)

            # 2️⃣ Si no hay, preguntar a la IA
            if not respuesta:
                respuesta = ask_gemini(text)
                if not respuesta:
                    respuesta = (
                        "No cuento con esa información, pero puedo consultar con el departamento correspondiente."
                    )

            # 3️⃣ Enviar respuesta al usuario
            send_whatsapp_message(from_number, respuesta)
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")

    return "EVENT_RECEIVED", 200


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    sys.stdout.flush()
    print(f"🚀 Iniciando Chatbot IA Empresarial en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

