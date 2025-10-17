from flask import Flask, request, jsonify
import os
import json
from meta_whatsapp import send_whatsapp_message
from ia_handler import load_knowledge_base, find_best_answer
from questionnaire import buscar_respuesta
from gemini_handler import ask_gemini

# ==========================================================
# CONFIGURACIÓN INICIAL
# ==========================================================
app = Flask(__name__)

# Mantener EXACTAMENTE estos nombres de variables de entorno
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "ICONSA")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "icon_sa_token")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")   # usado internamente por meta_whatsapp.py
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

# (Opcionales para otras funciones futuras — los respetamos aunque no se usen aquí)
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DRIVE_FOLDER_ID_USUARIOS_SG = os.getenv("DRIVE_FOLDER_ID_USUARIOS_SG")
DER_ID_USUARIOS_CESANTES = os.getenv("DER_ID_USUARIOS_CESANTES")

# Cargar base de conocimiento en memoria
try:
    KB = load_knowledge_base()
except Exception as e:
    print("⚠️ No se pudo cargar knowledge_base.json:", e)
    KB = []

# ==========================================================
# UTILIDAD: extraer texto del payload de WhatsApp
# ==========================================================
def extract_text(payload: dict) -> tuple[str, str] | tuple[None, None]:
    \"\"\"Devuelve (wa_id, texto) o (None, None) si no hay mensaje.\"\"\"
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return None, None

        msg = messages[0]
        wa_id = msg.get("from")

        # tipo texto estándar
        if msg.get("type") == "text":
            texto = msg.get("text", {}).get("body", "")

        # botones/interactive
        elif msg.get("type") == "interactive":
            interactive = msg.get("interactive", {})
            if interactive.get("type") == "button_reply":
                texto = interactive.get("button_reply", {}).get("title", "")
            elif interactive.get("type") == "list_reply":
                texto = interactive.get("list_reply", {}).get("title", "")
            else:
                texto = ""
        else:
            texto = ""

        return wa_id, (texto or "").strip()
    except Exception as e:
        print("❌ Error extrayendo texto:", e)
        return None, None

# ==========================================================
# VERIFICACIÓN DEL WEBHOOK (GET)
# ==========================================================
@app.route("/webhook", methods=["GET"])
@app.route("/whatsapp/webhook", methods=["GET"])
def verificar():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado.")
        return challenge, 200
    print("❌ Verificación fallida.")
    return "Error de verificación", 403

# ==========================================================
# RECEPCIÓN DE MENSAJES (POST)
# ==========================================================
@app.route("/webhook", methods=["POST"])
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    print("\\n================ NUEVO EVENTO ================")
    raw_body = request.get_data(as_text=True)
    print("RAW:", raw_body[:2000])

    try:
        data = request.get_json(force=True, silent=True) or json.loads(raw_body)
    except Exception as e:
        print("❌ JSON inválido:", e)
        return "EVENT_RECEIVED", 200

    print("JSON:", json.dumps(data, ensure_ascii=False, indent=2))

    wa_id, texto = extract_text(data)
    if not wa_id or not texto:
        print("⚠️ No hay mensaje de texto en el payload.")
        return "EVENT_RECEIVED", 200

    # 1) Heurística simple por secciones predefinidas (questionnaire.py)
    respuesta = buscar_respuesta(texto)

    # 2) Base de conocimiento (knowledge_base.json)
    if not respuesta and KB:
        kb_res = find_best_answer(texto, KB)
        respuesta = kb_res.get("texto")

    # 3) Gemini (fallback)
    if not respuesta:
        respuesta = ask_gemini(texto) or \
            "Actualmente no cuento con esa información, pero puedo escalar tu consulta al departamento correspondiente."

    # Firma/branding
    if BUSINESS_NAME:
        respuesta = f"{respuesta}\\n\\n— {BUSINESS_NAME} BOT"

    # Enviar respuesta
    try:
        send_whatsapp_message(wa_id, respuesta)
    except Exception as e:
        print("❌ Error enviando respuesta:", e)

    return "EVENT_RECEIVED", 200

# ==========================================================
# RUTA RAÍZ
# ==========================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "bot": f"{BUSINESS_NAME} BOT", "debug": DEBUG}), 200

# ==========================================================
# MAIN (para ejecución local)
# ==========================================================
if __name__ == "__main__":
    print(f"🚀 Iniciando {BUSINESS_NAME} BOT en {HOST}:{PORT} (debug={DEBUG})")
    app.run(host=HOST, port=PORT, debug=DEBUG)
