# app.py (Diagnóstico)
import os
import requests
from flask import Flask, request, jsonify

# =========================================
# CONFIGURACIÓN DE VARIABLES
# =========================================
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"  # tu número de WhatsApp
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)

# =========================================
# FUNCIÓN SIMPLE PARA ENVIAR MENSAJES
# =========================================
def enviar_mensaje(destinatario, texto):
    """
    Envía un mensaje directo de texto a WhatsApp para probar la API.
    """
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

    response = requests.post(WHATSAPP_URL, headers=headers, json=data)
    print(f"📤 Intentando enviar a {destinatario}: {texto}")
    print(f"🔎 Respuesta Meta: {response.status_code} - {response.text}")


# =========================================
# WEBHOOK POST
# =========================================
@app.route("/whatsapp/webhook", methods=["POST"])
def recibir_mensaje():
    """
    Cuando Meta envía un mensaje, este webhook lo recibe.
    """
    try:
        data = request.get_json()
        print("📨 Payload recibido:", data)

        # Si hay mensajes entrantes
        if data.get("object") == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    for msg in messages:
                        numero = msg.get("from")
                        texto = msg.get("text", {}).get("body", "")

                        print(f"📩 Mensaje recibido desde {numero}: {texto}")

                        # ENVÍA MENSAJE DE PRUEBA AUTOMÁTICO
                        enviar_mensaje(numero, "✅ Bot conectado correctamente con WhatsApp Cloud API.")

        return "EVENT_RECEIVED", 200

    except Exception as e:
        print("❌ Error en webhook:", e)
        return jsonify({"error": str(e)}), 500


# =========================================
# WEBHOOK GET (VERIFICACIÓN)
# =========================================
@app.route("/whatsapp/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Verificación de webhook exitosa.")
        return challenge, 200
    else:
        print("❌ Falló la verificación del webhook.")
        return "Error de verificación", 403


# =========================================
# SERVIDOR LOCAL
# =========================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "diagnostic bot"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Iniciando bot de diagnóstico en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
