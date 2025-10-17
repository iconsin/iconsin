import os
import google.generativeai as genai

# Mantener nombre de variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # No lanzamos excepción dura para no tumbar el contenedor: devolvemos None en llamadas
    print("⚠️ GEMINI_API_KEY no está definido. El bot funcionará solo con la base de conocimiento.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Model recomendado por google-generativeai >=0.8.x
MODEL_NAME = "gemini-1.5-flash"

def ask_gemini(pregunta: str) -> str | None:
    if not GEMINI_API_KEY:
        return None
    try:
        modelo = genai.GenerativeModel(MODEL_NAME)
        prompt = f"""
Eres el asistente oficial de {os.getenv('BUSINESS_NAME', 'ICONSA')}.
Responde SIEMPRE en español, profesional y conciso. Si no sabes la respuesta, sugiere escalar al área correspondiente.
Consulta del cliente: \"{pregunta}\"
"""
        res = modelo.generate_content(prompt)
        return (res.text or "").strip() if hasattr(res, "text") else None
    except Exception as e:
        print(f"⚠️ Error en Gemini: {e}")
        return None
