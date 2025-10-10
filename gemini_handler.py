# gemini_handler.py
def chat_answer(prompt: str, business_name: str = "ICONSA") -> str:
    """
    Simula respuesta inteligente (si no hay Gemini configurado).
    En producción puedes reactivar Gemini API.
    """
    try:
        prompt = prompt.lower()
        if "hola" in prompt:
            return f"¡Hola! 👋 Soy el asistente virtual de {business_name}. ¿Cómo puedo ayudarte hoy?"
        elif "gracias" in prompt:
            return "¡Con gusto! 😊 Si necesitas algo más, estoy aquí."
        elif "adiós" in prompt or "chau" in prompt:
            return "Hasta pronto 👋, fue un placer ayudarte."
        else:
            return f"Recibí tu mensaje: '{prompt}'. En breve te responderá un asesor de {business_name}."
    except Exception as e:
        print(f"⚠️ Error generando respuesta: {e}")
        return f"Hola, soy el asistente de {business_name}. ¿En qué puedo ayudarte?"
