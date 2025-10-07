
import requests
import os

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"

class WhatsAppClient:
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_text(self, to: str, text: str):
        url = f"{GRAPH_API_BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text[:4096]}
        }
        r = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if not r.ok:
            print("WA send_text error:", r.status_code, r.text)
        return r.ok

    def send_document_url(self, to: str, link: str, filename: str = None, caption: str = None):
        url = f"{GRAPH_API_BASE}/{self.phone_number_id}/messages"
        doc = {"link": link}
        if filename:
            doc["filename"] = filename
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": doc
        }
        if caption:
            payload["document"]["caption"] = caption[:1024]
        r = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if not r.ok:
            print("WA send_document_url error:", r.status_code, r.text)
        return r.ok
