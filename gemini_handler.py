
import os, json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

SYSTEM_CLASSIFIER = (
    "Eres un clasificador de intención para un bot empresarial. "
    "Dado un mensaje de usuario, responde SOLO JSON con el formato: "
    "{\"intent\": \"doc_request\" | \"chat\", \"keywords\": [<palabras clave>]} "
    "Indica 'doc_request' cuando pida enviar/buscar/mostrar un documento, contrato, factura, política, catálogo, etc. "
    "Las 'keywords' deben ser útiles para buscar archivos en Google Drive."
)

SYSTEM_ASSISTANT = (
    "Eres un asistente de atención al cliente de {business}. "
    "Responde en español, breve y útil. Si hay dudas, pide aclaraciones."
)

def classify_intent(user_text: str) -> dict:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""{SYSTEM_CLASSIFIER}
Usuario: {user_text}
JSON:"""
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # Intenta parsear JSON estrictamente
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end]) if start != -1 else {"intent": "chat", "keywords": []}
        if "intent" not in data:
            data["intent"] = "chat"
        if "keywords" not in data or not isinstance(data["keywords"], list):
            data["keywords"] = []
        return data
    except Exception as e:
        print("Gemini classify error:", e)
        return {"intent": "chat", "keywords": []}

def chat_answer(user_text: str, business_name: str = "Mi Empresa") -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        system = SYSTEM_ASSISTANT.format(business=business_name)
        resp = model.generate_content(f"""{system}
Usuario: {user_text}
Asistente:""" )
        return (resp.text or "").strip() or "¿Podrías repetir, por favor?"
    except Exception as e:
        print("Gemini chat error:", e)
        return "Lo siento, ahora mismo no puedo responder. Intenta más tarde."
