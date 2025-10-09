import os
import json
import random
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

SYSTEM_CLASSIFIER = (
    "Eres un clasificador de intención para un bot empresarial. "
    "Dado un mensaje de usuario, responde SOLO JSON con el formato: "
    '{"intent": "doc_request" | "chat", "keywords": ["..."]}. '
    "Usa 'doc_request' cuando el usuario pida enviar, buscar o mostrar un documento, contrato, política, informe, catálogo, etc. "
    "Las 'keywords' deben ser útiles para buscar archivos en Google Drive. "
    "Si el texto no se relaciona con documentos, marca 'intent':'chat'."
)

SYSTEM_ASSISTANT = (
    "Eres un asistente de atención al cliente de {business}. "
    "Responde en español, breve y formal. "
    "⚠️ IMPORTANTE: Nunca inventes datos ni afirmaciones. "
    "Si no tienes información sobre algo, dilo claramente y ofrece buscarlo o consultarlo. "
    "Usa un tono empático, no repetitivo."
)

def classify_intent(user_text: str) -> dict:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""{SYSTEM_CLASSIFIER}
Usuario: {user_text}
JSON:"""
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        start, end = text.find("{"), text.rfind("}") + 1
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
    """
    Genera una respuesta conversacional breve y útil.
    No inventa información: si Gemini devuelve algo vacío o ambiguo,
    se genera una frase alternativa más humana.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        system = SYSTEM_ASSISTANT.format(business=business_name)
        resp = model.generate_content(f"""{system}
Usuario: {user_text}
Asistente:""")
        answer = (resp.text or "").strip()

        # Si Gemini no respondió, o respondió sin contexto, usa un fallback natural
        if not answer or len(answer) < 5:
            fallbacks = [
                "No tengo información precisa sobre eso, ¿quieres que lo busque en internet?",
                "No estoy seguro, pero puedo ayudarte a buscarlo si lo deseas.",
                "Lo siento, no tengo una respuesta exacta. ¿Deseas que intente buscarla en línea?",
                "No dispongo de esa información, pero puedo consultar fuentes externas.",
                "No cuento con datos sobre eso. ¿Te gustaría que intente buscarlo?"
            ]
            return random.choice(fallbacks)

        # Evita respuestas inventadas o genéricas
        invalids = ["no tengo", "no sé", "no dispongo", "no cuento", "no puedo"]
        if any(w in answer.lower() for w in invalids):
            return random.choice([
                "No tengo información exacta sobre eso, pero puedo intentar buscarla.",
                "No dispongo de esa información en mis registros. ¿Quieres que la busque en internet?",
                "No estoy seguro de ese dato, pero puedo consultar fuentes externas."
            ])

        return answer

    except Exception as e:
        print("Gemini chat error:", e)
        return random.choice([
            "No puedo responder en este momento, pero puedo intentar buscarlo más tarde.",
            "Hubo un problema con la conexión. ¿Deseas que intente buscar en internet?",
            "Disculpa, no tengo esa información disponible ahora."
        ])
