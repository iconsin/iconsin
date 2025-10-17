from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import os

# ==============================
# CONFIGURACIÓN
# ==============================
app = Flask(__name__)

# Tokens y claves (se definen en Render → Environment variables)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "icon_sa_token")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "TU_TOKEN_FACEBOOK")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "TU_PHONE_NUMBER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TU_API_KEY_GEMINI")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel("gemini-1.0-pro")

# ==============================
# FUNCIÓN PARA ENVIAR MENSAJE A WHATSAPP
# ==============================
def enviar_mensaje(wa_id, texto):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "text",
        "text": {"body": texto}
    }
    r = requests.post(url, headers=headers, json=data)
    print("📤 Enviado:", r.status_code, r.text)

# ==============================
# VERIFICACIÓN DEL WEBHOOK (Meta)
# ==============================
@app.route("/webhook", methods=["GET"])
def verificar():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge, 200
    else:
        print("❌ Error en verificación de webhook.")
        return "Error de verificación", 403

# ==============================
# RECEPCIÓN DE MENSAJES
# ==============================
@app.route("/webhook", methods=["GET", "POST"])
@app.route("/whatsapp/webhook", methods=["GET", "POST"])
def webhook():
    ...

    data = request.get_json()
    print("📩 Datos recibidos:", data)

    try:
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        wa_id = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        nombre = data["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    except Exception as e:
        print("⚠️ No se encontró mensaje de texto:", e)
        return jsonify({"status": "no message"}), 200

    # ==============================
    # RESPUESTA CON GEMINI
    # ==============================
    prompt = f"""
    Eres ICONSA BOT, el asistente virtual de la empresa ICONSA.
    ICONSA ofrece soporte técnico, redes, y soluciones IT en Panamá.
    Responde siempre de forma profesional, breve y cordial.
    El cliente se llama {nombre} y ha dicho: "{mensaje}".
    """

    try:
        respuesta_gemini = modelo.generate_content(prompt)
        respuesta = respuesta_gemini.text.strip()
    except Exception as e:
        print("❌ Error al generar respuesta con Gemini:", e)
        respuesta = "Tuve un problema para procesar la respuesta, pero puedo reenviar tu consulta al departamento correspondiente."

    enviar_mensaje(wa_id, respuesta)
    return jsonify({"status": "message sent"}), 200

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto que Render asigne
    app.run(host="0.0.0.0", port=port)
