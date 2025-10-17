from flask import Flask, request, jsonify
import os
import json
from meta_whatsapp import send_whatsapp_message
from ia_handler import load_knowledge_base, find_best_answer
from questionnaire import buscar_respuesta
from gemini_handler import ask_gemini

app = Flask(__name__)

BUSINESS_NAME = os.getenv("BUSINESS_NAME", "ICONSA")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "icon_sa_token")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

def extract_text(payload: dict):
    """Devuelve (wa_id, texto) o (None, None) si no hay mensaje."""
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return None, None
        msg = messages[0]
        wa_id = msg.get("from")
        texto = ""
        if msg.get("type") == "text":
            texto = msg.get("text", {}).get("body", "")
        elif msg.get("type") == "interactive":
            interactive = msg.get("interactive", {})
            if interactive.get("type") == "button_reply":
                texto = interactive.get("button_reply", {}).get("title", "")
            elif interactive.get("type") == "list_reply":
                texto = interactive.get("list_reply", {}).get("title", "")
        return wa_id, texto.strip()
    except Exception as e:
        print("Error extrayendo texto:", e)
        return None, None

@app.route("/whatsapp/webhook", methods=["GET"])
def verificar():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Error de verificación", 403

@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    wa_id, texto = extract_text(data or {})
    if not wa_id or not texto:
        return "EVENT_RECEIVED", 200

    respuesta = buscar_respuesta(texto)
    if not respuesta:
        kb = load_knowledge_base()
        kb_res = find_best_answer(texto, kb)
        respuesta = kb_res.get("texto")
    if not respuesta:
        respuesta = ask_gemini(texto) or "Actualmente no tengo respuesta, consultaré al área correspondiente."
    if BUSINESS_NAME:
        respuesta = f"{respuesta}\n\n— {BUSINESS_NAME} BOT"
    send_whatsapp_message(wa_id, respuesta)
    return "EVENT_RECEIVED", 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
