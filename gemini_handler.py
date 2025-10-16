import os
import google.generativeai as genai

# Configuración
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ Falta la variable de entorno GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(pregunta: str) -> str:
    """
    Envía una pregunta a Gemini y devuelve una respuesta procesada en texto.
    Si ocurre un error, devuelve None.
    """
    try:
        contexto = f"""
        Eres ICONSA BOT, el asistente técnico oficial de ICONSA Panamá.
        ICONSA brinda servicios de soporte técnico, redes, servidores, licencias y gestión IT.
        Responde SIEMPRE en español, de forma profesional, empática y concisa.
        Cliente: {pregunta}
        """

        respuesta = model.generate_content(contexto)
        texto = respuesta.text.strip() if respuesta and respuesta.text else None
        return texto
    except Exception as e:
        print(f"⚠️ Error en Gemini: {e}")
        return None

