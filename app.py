from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- Config ---
VERIFY_TOKEN = "123456"  # usa el mismo que pusiste en Meta
ACCESS_TOKEN = "EA..."   # tu token de acceso de WhatsApp Cloud

@app.route("/whatsapp/webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        # Validación del webhook
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Token inválido", 403

    if request.method == "POST":
        data = request.get_json()
        print("📩 Datos recibidos:", data)

        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            phone_id = data["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]
            from_number = message["from"]
            msg_body = message["text"]["body"]

            print(f"Mensaje recibido de {from_number}: {msg_body}")

            # Responder a WhatsApp
            send_message(phone_id, from_number, "✅ Recibido correctamente en el servidor Flask.")

        except Exception as e:
            print("Error procesando mensaje:", e)

        return jsonify({"status": "ok"}), 200

def send_message(phone_id, to, text):
    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
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

    r = requests.post(url, headers=headers, json=payload)
    print("Respuesta de Meta:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)


