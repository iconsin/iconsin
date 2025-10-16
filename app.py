import os
import requests
from flask import Flask, request, jsonify
from ia_handler import load_knowledge_base, find_best_answer

ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token"
WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)
knowledge_base = load_knowledge_base()

# Enviar mensaje a WhatsApp
def send_whatsapp_message(to, text):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(WHATSAPP_URL, headers=headers, json=data)

# Webhook GET (verificación)
@app.route("/whatsapp/webhook", methods=["GET"])
def verify_token():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Error de verificación", 403

# Webhook POST (mensajes)
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        text = msg["text"]["body"]

        respuesta = find_best_answer(text, knowledge_base)
        send_whatsapp_message(from_number, respuesta["texto"])

        print(f"💬 {from_number}: {text} → 🧠 {respuesta['texto']}")
    except Exception as e:
        print("⚠️ Error procesando mensaje:", e)
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "bot": "IA Empresarial"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



