# gemini_handler.py
import os
import google.generativeai as genai
from openai import OpenAI

# ============================================================
# CONFIGURACIÓN AUTOMÁTICA SEGÚN EL MODELO DISPONIBLE
# ============================================================
USE_GEMINI = os.getenv("GEMINI_API_KEY") is not None
USE_OPENAI = os.getenv("OPENAI_API_KEY") is not None

if USE_GEMINI:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
elif USE_OPENAI:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    raise Exception("⚠️ No hay ninguna API key configurada (GEMINI o OPENAI).")

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def chat_answer(prompt: str, business_name: str = "ICONSA") -> str:
    """
    Devuelve una respuesta generada por IA.
    Si hay problema con Gemini u OpenAI, devuelve un mensaje de error.
    """
    try:
        prompt = prompt.strip()
        if not prompt:
            return "No recibí texto para procesar. ¿Podrías repetirlo?"

        # Gemini
        if USE_GEMINI:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(
                f"Eres un asistente virtual de {business_name}. Responde de forma natural y profesional al mensaje del usuario:\n\n{prompt}"
            )
            return response.text.strip()

        # OpenAI
        elif USE_OPENAI:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Eres un asistente virtual de {business_name}, amable y útil."},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content.strip()

        else:
            return "No hay modelo de IA activo."

    except Exception as e:
        print(f"❌ Error en chat_answer: {e}")
        return "Ocurrió un problema al generar la respuesta con la IA."
