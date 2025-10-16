import os
import requests
import json

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
    raise ValueError("❌ Faltan variables de entorno META_ACCESS_TOKEN o PHONE_NUMBER_ID")

def send_whatsapp_message(to_number: str, message: str):
    """
    Envía un mensaje de texto por WhatsApp Cloud API al número indicado.
    """
    try:
        url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
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

        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"⚠️ Error enviando mensaje: {response.status_code} - {response.text}")
        else:
            print(f"✅ Mensaje enviado correctamente a {to_number}")
    except Exception as e:
        print(f"❌ Excepción al enviar mensaje: {e}")
