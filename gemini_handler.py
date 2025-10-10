# gemini_handler.py
def chat_answer(prompt: str, business_name: str = "ICONSA") -> str:
    """
    Simula respuesta IA (sin depender aún de la API de Gemini)
    """
    try:
        text = prompt.lower()
        if "hola" in text:
            return f"¡Hola! 👋 Soy el asistente virtual de {business_name}. ¿Cómo puedo ayudarte hoy?"
        elif "gracias" in text:
            return "¡Con gusto! 😊 ¿Hay algo más en lo que pueda ayudarte?"
        elif "adiós" in text or "chau" in text:
            return "Hasta pronto 👋, ¡fue un placer ayudarte!"
        else:
            return f"Recibí tu mensaje: '{prompt}'. En breve te responderá un asesor de {business_name}."
    except Exception as e:
        print(f"⚠️ Error en chat_answer: {e}")
        return f"Hola 👋, soy el asistente de {business_name}. ¿En qué puedo ayudarte?"
