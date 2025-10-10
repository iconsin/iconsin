# ==========================================================
# ICONSA WhatsApp Bot (versión de depuración completa)
# ==========================================================
import os
import requests
from flask import Flask, request, jsonify
from gemini_handler import chat_answer

# ----------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# ----------------------------------------------------------
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"
BUSINESS_NAME = os.getenv("BUSINESS_NAME") or "ICONSA"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"


# ----------------------------------------------------------
# FUNCIÓN PARA ENVIAR MENSAJES
# ----------------------------------------------------------
def send_whatsapp_message(to, text):
    """
    Envía un mensaje de texto a un número de WhatsApp.
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

        r = requests.post(WHATSAPP_URL, headers=headers, json=payload)
        print(f"📤 Enviado a {to}: {text}")
        print(f"🔎 Respuesta Meta: {r.status_code} - {r.text}")

        if r.status_code != 200:
            print("⚠️ Error al enviar mensaje a WhatsApp")

    except Exception as e:
        print(f"❌ Error en send_whatsapp_message: {e}")


# ----------------------------------------------------------
# WEBHOOK PARA RECIBIR MENSAJES (POST)
# ----------------------------------------------------------
@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    """
    Recibe mensajes desde la Cloud API de WhatsApp.
    """
    data = request.get_json(force=True, silent=True)
    print("\n📬 === NUEVO EVENTO RECIBIDO ===")
    print(data)

    try:
        entry = (data.get("entry") or [{}])[0]
        changes = (entry.get("changes") or [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            print("📭 Evento sin campo 'messages' (probablemente status update)")
            return "EVENT_RECEIVED", 200

        msg = messages[0]
        user_number = msg.get("from")
        msg_type = msg.get("type", "")
        text_body = ""

        if msg_type == "text":
            text_body = msg.get("text", {}).get("body", "").strip()
        elif msg_type == "interactive":
            interactive = msg.get("interactive", {})
            text_body = (
                (interactive.get("button_reply", {}) or {}).get("title")
                or (interactive.get("list_reply", {}) or {}).get("title")
                or ""
            )

        print(f"💬 Mensaje recibido de {user_number}: {text_body}")

        if not text_body:
            print("🕳 El mensaje no tiene texto (puede ser imagen o botón vacío).")
            return "EVENT_RECEIVED", 200

        # --------------------------------------------------
        # Procesamiento con IA (Gemini)
        # --------------------------------------------------
        try:
            respuesta = chat_answer(text_body, business_name=BUSINESS_NAME)
        except Exception as e:
            print(f"⚠️ Error en chat_answer: {e}")
            respuesta = f"Hola 👋, soy el asistente de {BUSINESS_NAME}. ¿En qué puedo ayudarte?"

        print(f"🤖 Respuesta generada: {respuesta}")
        send_whatsapp_message(user_number, respuesta)

        return "EVENT_RECEIVED", 200

    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# VERIFICACIÓN DEL WEBHOOK (GET)
# ----------------------------------------------------------
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


# ----------------------------------------------------------
# RUTA DE ESTADO
# ----------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "ICONSA WhatsApp Bot",
        "version": "debug-1.0"
    })


# ----------------------------------------------------------
# INICIO DEL SERVIDOR
# ----------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando ICONSA WhatsApp Bot en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
