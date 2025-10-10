# app.py
from flask import Flask, request, jsonify
import os
from gemini_handler import chat_answer
from whatsapp_api_client_python import API as WhatsAppAPI

app = Flask(__name__)

# ============================================================
# CONFIGURACIÓN DE VARIABLES
# ============================================================
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "TU_TOKEN_PERMANENTE_AQUI"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "25681420111462727"  # ID de tu número
BUSINESS_NAME = "ICONSA"

wa = WhatsAppAPI(token=ACCESS_TOKEN)

# ============================================================
# WEBHOOK PRINCIPAL (POST)
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

        message = messages[0]
        from_wa = message["from"]  # número del usuario
        text_body = message["text"]["body"] if "text" in message else ""

        if text_body:
            print(f"🤖 Procesando mensaje: {text_body}")
            ai_response = chat_answer(text_body, business_name=BUSINESS_NAME)
            print(f"🧠 Respuesta IA: {ai_response}")

            wa.send_message(phone_number_id=PHONE_NUMBER_ID, to=from_wa, text=ai_response)

        return "EVENT_RECEIVED", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================
# VERIFICACIÓN DEL WEBHOOK (GET)
# ============================================================
@app.route("/whatsapp/webhook", methods=["GET"])
def verify_token():
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge, 200
    else:
        print("❌ Error al verificar el webhook.")
        return "Error de verificación", 403


# ============================================================
# EJECUCIÓN DEL SERVIDOR LOCAL
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
