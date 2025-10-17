from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import os
import json

# ==========================================================
# CONFIGURACIÓN INICIAL
# ==========================================================
app = Flask(__name__)

# Variables de entorno (Render → Environment Variables)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "icon_sa_token")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "TU_TOKEN_FACEBOOK")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "TU_PHONE_NUMBER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TU_API_KEY_GEMINI")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel("gemini-1.5-flash")

# ==========================================================
# FUNCIÓN PARA ENVIAR MENSAJES A WHATSAPP
# ==========================================================
def enviar_mensaje(wa_id, texto):
    """Envía un mensaje de texto a través de la API de WhatsApp Cloud."""
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
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

    try:
        r = requests.post(url, headers=headers, json=data)
        print(f"📤 Enviado a {wa_id}: {texto}")
        print("🔎 Respuesta de Meta:", r.status_code, "-", r.text)
    except Exception as e:
        print("❌ Error enviando mensaje:", e)

# ==========================================================
# VERIFICACIÓN DEL WEBHOOK (GET)
# ==========================================================
@app.route("/webhook", methods=["GET"])
@app.route("/whatsapp/webhook", methods=["GET"])
def verificar():
    """Verifica la conexión del webhook con Meta."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge, 200
    else:
        print("❌ Error de verificación de webhook.")
        return "Error de verificación", 403

# ==========================================================
# RECEPCIÓN DE MENSAJES (POST)
# ==========================================================
@app.route("/webhook", methods=["POST"])
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    """Procesa mensajes entrantes de WhatsApp."""
    print("\n📬 === NUEVO EVENTO RECIBIDO ===")

    # Leer el cuerpo crudo del request
    raw = request.get_data(as_text=True)
    print("🔹 Cuerpo RAW recibido:\n", raw if raw.strip() else "(vacío)")

    # Intentar decodificar JSON
    try:
        data = request.get_json(force=True)
        print("\n🔹 JSON decodificado:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("❌ Error al decodificar JSON:", e)
        return jsonify({"status": "invalid json"}), 200

    # Extraer datos del mensaje entrante
    try:
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        wa_id = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        nombre = data["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

        print(f"📩 MENSAJE DETECTADO de {nombre} ({wa_id}): {mensaje}")
    except Exception as e:
        print("⚠️ No se encontró mensaje de texto:", e)
        return jsonify({"status": "no message"}), 200

    # ==========================================================
    # RESPUESTA CON IA (GEMINI)
    # ==========================================================
    prompt = f"""
    Eres ICONSA BOT, el asistente virtual inteligente de la empresa ICONSA.
    ICONSA ofrece soporte técnico, redes, y soluciones IT en Panamá.

    - Responde de forma profesional, breve y cordial.
    - Si la pregunta se relaciona con RRHH, contabilidad, soporte o ISO, responde acorde.
    - Si no tienes la información, responde:
      "Actualmente no cuento con esa información, pero puedo escalar tu consulta al departamento correspondiente."

    Cliente: {nombre}
    Mensaje recibido: "{mensaje}"
    """

    try:
        respuesta_gemini = modelo.generate_content(prompt)
        respuesta = respuesta_gemini.text.strip() if respuesta_gemini.text else "No logré generar una respuesta."
    except Exception as e:
        print("❌ Error al generar respuesta con Gemini:", e)
        respuesta = "Tuve un problema para procesar tu mensaje, pero puedo reenviar tu consulta al área correspondiente."

    # Enviar la respuesta al usuario
    enviar_mensaje(wa_id, respuesta)

    return jsonify({"status": "message sent"}), 200

# ==========================================================
# RUTA RAÍZ DE PRUEBA
# ==========================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "bot": "ICONSA BOT con IA activo"}), 200

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando Chatbot IA Empresarial en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
