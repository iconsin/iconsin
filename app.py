
import os, json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from state_store import StateStore
from meta_whatsapp import WhatsAppClient
from questionnaire import Questionnaire
from gemini_handler import classify_intent, chat_answer
from drive_client import search_files, ensure_anyone_reader, get_best_link

load_dotenv()

app = Flask(__name__)

# -------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# -------------------------------------------------------
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "verify-token")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Mi Empresa")
DRIVE_FOLDERS = [
    os.getenv("DRIVE_FOLDER_ID_USUARIOS_CESANTES"),
    os.getenv("DRIVE_FOLDER_ID_USUARIOS_SG")
]

# -------------------------------------------------------
# FUNCIÓN AUXILIAR PARA BUSCAR EN VARIAS CARPETAS
# -------------------------------------------------------
def search_all_folders(keywords):
    results = []
    for fid in DRIVE_FOLDERS:
        if fid:
            results.extend(search_files(keywords, folder_id=fid, max_results=3))
    return results


# -------------------------------------------------------
# INICIALIZACIÓN DE COMPONENTES
# -------------------------------------------------------
store = StateStore(os.getenv("DATABASE_URL", "sqlite:///data/bot.db"))

wa = WhatsAppClient(
    access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
    phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
)

qflow = Questionnaire(store=store)


# -------------------------------------------------------
# ENDPOINT RAÍZ
# -------------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "ok": True,
        "service": "WhatsApp Gemini+Drive Bot",
        "business": BUSINESS_NAME
    })


# -------------------------------------------------------
# ENDPOINT WEBHOOK (GET para verificación, POST para mensajes)
# -------------------------------------------------------
@app.route("/whatsapp/webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verificado correctamente.")
            return challenge, 200
        print("❌ Falló la verificación del webhook.")
        return "Verification failed", 403

    payload = request.get_json(force=True, silent=True) or {}
    entries = payload.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                process_incoming(message, value)
    return jsonify({"status": "received"}), 200


# -------------------------------------------------------
# PROCESAR MENSAJE ENTRANTE
# -------------------------------------------------------
def process_incoming(message, envelope):
    from_wa = message.get("from")
    msg_type = message.get("type", "text")
    text_body = None

    if msg_type == "text":
        text_body = (message.get("text", {}) or {}).get("body", "").strip()

    elif msg_type == "interactive":
        # botones / listas
        interactive = message.get("interactive", {})
        text_body = (
            (interactive.get("button_reply", {}) or {}).get("title")
            or (interactive.get("list_reply", {}) or {}).get("title")
            or ""
        )

    else:
        text_body = ""

    # 1️⃣ Verificar si el mensaje pertenece al cuestionario
    reply = qflow.handle_message(user_id=from_wa, message=text_body)
    if reply:
        wa.send_text(to=from_wa, text=reply)
        return

    # 2️⃣ Clasificar intención con Gemini
    intent = classify_intent(text_body or "")
    if intent.get("intent") == "doc_request":
        keywords = intent.get("keywords") or []
        if not keywords:
            wa.send_text(
                to=from_wa,
                text="¿Qué documento necesitas exactamente? (ej: 'contrato de alquiler 2025')"
            )
            return

        files = search_all_folders(keywords)
        if not files:
            wa.send_text(
                to=from_wa,
                text="No encontré documentos con esos criterios. ¿Puedes darme otro nombre o palabra clave?"
            )
            return

        # Intentamos compartir y enviar enlaces
        for f in files:
            try:
                ensure_anyone_reader(f["id"])
            except Exception as e:
                print(f"⚠️ No se pudo cambiar permisos del archivo: {f['name']} - {e}")

            link = get_best_link(f)
            caption = f"📄 {f['name']}"
            wa.send_document_url(
                to=from_wa,
                link=link,
                filename=f.get("name"),
                caption=caption
            )
        return

    # 3️⃣ Si no hay intención de documento → Chat general con Gemini
    answer = chat_answer(text_body or "", business_name=BUSINESS_NAME)
    wa.send_text(to=from_wa, text=answer)


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    print(f"🚀 Iniciando WhatsApp Gemini+Drive Bot en {host}:{port}")
    app.run(host=host, port=port, debug=debug)
