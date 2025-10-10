# gemini_handler.py
import google.generativeai as genai
import os

# Configura la clave de API de Gemini (si existe)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
else:
    print("⚠️ GEMINI_API_KEY no configurada. Se usarán respuestas por defecto.")

def chat_answer(prompt: str, business_name: str = "ICONSA") -> str:
    """
    Procesa una pregunta con Gemini. Si no hay clave o hay error,
    responde con un mensaje base genérico.
    """
    try:
        if not GEMINI_KEY:
            raise ValueError("No hay clave de Gemini configurada")

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Eres el asistente virtual de {business_name}. "
                                          f"Responde de forma profesional y breve: {prompt}")
        if response and response.text:
            return response.text.strip()
        else:
            return "Lo siento, no pude generar una respuesta en este momento."
    except Exception as e:
        print(f"⚠️ Error en Gemini: {e}")
        # Respuesta por defecto si algo falla
        return f"Soy el asistente virtual de {business_name}. ¿Podrías reformular tu consulta?"
