# gemini_handler.py
import os
import google.generativeai as genai

# ============================================================
# CONFIGURACIÓN DE GEMINI
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("⚠️ No se encontró la variable GEMINI_API_KEY en el entorno.")

genai.configure(api_key=GEMINI_API_KEY)

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def chat_answer(prompt: str, business_name: str = "ICONSA") -> str:
    """
    Genera una respuesta usando Gemini.
    """
    try:
        prompt = prompt.strip()
        if not prompt:
            return "No recibí texto para procesar. ¿Podrías repetirlo?"

        # Usa el modelo de texto de Gemini
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            f"Eres un asistente virtual de {business_name}. "
            f"Responde de forma natural, profesional y conversacional al siguiente mensaje:\n\n{prompt}"
        )

        # Si Gemini no devuelve texto, devolvemos algo genérico
        if not response or not response.text:
            return "No tengo una respuesta en este momento. ¿Podrías reformular tu pregunta?"

        return response.text.strip()

    except Exception as e:
        print(f"❌ Error en chat_answer: {e}")
        return "Ocurrió un problema al generar la respuesta con la IA."
