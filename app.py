# app.py (Diagnóstico final - modo RAYOS X)
import os
import requests
from flask import Flask, request, jsonify

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token_de_verificacion"

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)

def enviar_mensaje(destinatario, texto):
    """Envía un mensaje directo de texto a WhatsApp."""
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
    print(f"📤 Intentando enviar mensaje a {destinatario}: {texto}")
    r = requests.post(WHATSAPP_URL, headers=headers, json=data)
    print(f"🔎 Código HTTP: {r.status_code}")
    print(f"🔎 Respuesta Meta: {r.text}")

@app.route("/whatsapp/webhook", methods=["POST"])
def recibir_mensaje():
    print("📥 [1] Se recibió un POST en /whatsapp/webhook")

    # Capturamos el contenido crudo por si Meta no envía JSON bien formateado
    raw_data = request.data.decode("utf-8", errors="ignore")
    print("🧾 [2] Contenido RAW recibido:", raw_data)

    try:
        json_data = request.get_json(force=True, silent=False)
        print("📦 [3] JSON parseado correctamente:", json_data)
    except Exception as e:
        print(f"❌ [3] Error al parsear JSON: {e}")
        json_data = None

    # Si Meta manda el formato correcto, lo procesamos
    if json_data and json_data.get("object") == "whatsapp_business_account":
        for entry in json_data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    numero = msg.get("from")
                    texto = msg.get("text", {}).get("body", "")
                    print(f"📩 [4] MENSAJE DETECTADO: {texto} (de {numero})")
                    if numero:
                        enviar_mensaje(numero, "✅ Recibí tu mensaje correctamente.")
    else:
        print("⚠️ [4] No se detectó formato de mensaje válido en el JSON recibido.")

    print("✅ [5] Finalizando ciclo de recepción.")
    return "EVENT_RECEIVED", 200


@app.route("/whatsapp/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge, 200
    else:
        print("❌ Error de verificación del webhook.")
        return "Error de verificación", 403


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "diagnostic-xray"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Iniciando bot de diagnóstico RAYOS X en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

