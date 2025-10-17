import os
import requests

# Mantener EXACTAMENTE estos nombres
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
    raise ValueError("❌ Faltan variables de entorno: META_ACCESS_TOKEN o PHONE_NUMBER_ID")

GRAPH_VERSION = "v20.0"  # versión estable y reciente

def send_whatsapp_message(to_number: str, message: str):
    """
    Envía un mensaje de texto por WhatsApp Cloud API al número indicado.
    """
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    if resp.status_code >= 300:
        print(f"⚠️ Error Meta API {resp.status_code}: {resp.text}")
    else:
        print(f"✅ Mensaje enviado a {to_number}")
