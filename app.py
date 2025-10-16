import os
import requests
from flask import Flask, request, jsonify
from ia_handler import load_knowledge_base, find_best_answer

ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN") or "AQUI_TU_TOKEN_PERMANENTE"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") or "863388500182148"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "mi_token"
WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)
knowledge_base = load_knowledge_base()

def send_whatsapp_message(to, text):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    response = requests.post(WHATSAPP_URL, headers=headers, json=payload)
    print(f"📤 Enviado a {to}: {text}")
    print(f"🔎 Respuesta de Meta: {response.status_code} - {response.text}")

@app.route("/whatsapp/webhook", methods=["GET"])
def verify_token():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge, 200
    print("❌ Error de verificación del webhook.")
    return "Error de verificación", 403

@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        text = msg["text"]["body"].strip()
        respuesta = find_best_answer(text, knowledge_base)
        send_whatsapp_message(from_number, respuesta["texto"])
        print(f"💬 {from_number}: {text} → 🧠 {respuesta['texto']}")
    except Exception as e:
        print(f"⚠️ Error procesando mensaje: {e}")
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "bot": "Chatbot IA Empresarial"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
