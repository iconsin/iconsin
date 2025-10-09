import os
import json
import random
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from state_store import StateStore
from meta_whatsapp import WhatsAppClient
from questionnaire import Questionnaire
from gemini_handler import classify_intent, chat_answer
from drive_client import search_files, ensure_anyone_reader, get_best_link

load_dotenv()

app = Flask(__name__)

# ============================
# CONFIGURACIÓN GLOBAL
# ============================
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "verify-token")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Mi Empresa")
DRIVE_FOLDERS = [
    os.getenv("DRIVE_FOLDER_ID_USUARIOS_CESANTES"),
    os.getenv("DRIVE_FOLDER_ID_USUARIOS_SG")
]

# ============================
# FUNCIONES AUXILIARES
# ============================
def search_all_folders(keywords):
    """Busca documentos en todas las carpetas Drive configuradas"""
    results = []
    for fid in DRIVE_FOLDERS:
        if fid:
            results.extend(search_files(keywords, folder_id=fid, max_results=3))
    return results

def random_fallback():
    """Mensajes variados para cuando el bot no tiene información concreta"""
    frases = [
        "No tengo esa información en mis registros.",
        "Lo siento, no encuentro nada relacionado con eso.",
        "Esa respuesta no la tengo disponible por ahora.",
        "No cuento con datos sobre ese tema.",
        "No estoy seguro de eso, pero puedo intentar buscarlo."
    ]
    return random.choice(frases)

# ============================
# INSTANCIAS PRINCIPALES
# ============================
store = StateStore(os.getenv("DATABASE_URL", "sqlite:///data/bot.db"))
wa = WhatsAppClient(
    access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
    phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
)
qflow = Questionnaire(store=store)

# ============================
# ENDPOINT RAÍZ
# ============================
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "ok": True,
        "service": "WhatsApp Gemini+Drive Bot",
        "business": BUSINESS_NAME
    })

# ============================
# WEBHOOK DE META
# ============================
@app.route("/whatsapp/webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verificado correctamente.")
            return challenge, 200
        print("❌ Error: verificación fallida.")
        return "Verification failed", 403

    # POST - mensajes entrantes desde WhatsApp
    payload = request.get_json(force=True, silent=True) or {}
    print("📨 Payload recibido de Meta:\n", json.dumps(payload, indent=2))

    entries = payload.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            print("🔍 Mensajes detectados:", messages)
            for message in messages:
                process_incoming(message, value)

    return jsonify({"status": "received"}), 200

# ============================
# PROCESAMIENTO DE MENSAJES
# ============================
def process_incoming(message, envelope):
    from_wa = message.get("from")
    msg_type = message.get("type", "text")
    text_body = None

    print(f"\n📩 Mensaje entrante desde {from_wa} (tipo: {msg_type})")

    if msg_type == "text":
        text_body = (message.get("text", {}) or {}).get("body", "").strip()
    elif msg_type == "interactive":
        interactive = message.get("interactive", {})
        text_body = (
            (interactive.get("button_reply", {}) or {}).get("title")
            or (interactive.get("list_reply", {}) or {}).get("title")
            or ""
        )
    else:
        text_body = ""

    print(f"📝 Texto procesado: '{text_body}'")

    # 1️⃣ Revisión en cuestionario (solo si aplica)
    reply = qflow.handle_message(user_id=from_wa, message=text_body)
    if reply and not reply.lower().startswith(("lo siento", "en qué puedo ayudarte", "hola")):
        wa.send_text(to=from_wa, text=reply)
        print(f"🤖 Respuesta automática (cuestionario): {reply}")
        return

    # 2️⃣ Clasificar intención con Gemini
    intent = classify_intent(text_body or "")
    print(f"🎯 Intención detectada: {intent}")

    if intent.get("intent") == "doc_request":
        keywords = intent.get("keywords") or []
        if not keywords:
            wa.send_text(to=from_wa, text="¿Qué documento necesitas exactamente? (ej: 'contrato de alquiler 2025')")
            return

        files = search_all_folders(keywords)
        if not files:
            wa.send_text(to=from_wa, text="No encontré documentos con esos criterios. ¿Quieres que intente buscarlos en Drive?")
            return

        for f in files:
            try:
                ensure_anyone_reader(f["id"])
            except Exception as e:
                print("⚠️ No se pudo cambiar permisos del archivo:", e)
            link = get_best_link(f)
            caption = f"📄 {f['name']}"
            wa.send_document_url(to=from_wa, link=link, filename=f.get("name"), caption=caption)
            print(f"📤 Enviado documento: {f['name']}")
        return

    # 3️⃣ Chat general con Gemini (sin invenciones)
    answer = chat_answer(text_body or "", business_name=BUSINESS_NAME)
    if not answer or "no tengo" in answer.lower():
        final_text = f"{random_fallback()} ¿Deseas que busque la respuesta en internet?"
    else:
        final_text = answer

    wa.send_text(to=from_wa, text=final_text)
    print(f"💬 Respuesta generada: {final_text}")

# ============================
# INICIO DEL SERVIDOR
# ============================
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    print(f"🚀 Iniciando WhatsApp Gemini+Drive Bot en {host}:{port}")
    app.run(host=host, port=port, debug=debug)
