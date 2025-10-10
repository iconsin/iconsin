
# gemini_handler.py
from questionnaire import obtener_respuesta_automatica

def procesar_mensaje(texto_usuario):
    """
    Procesa el mensaje recibido y devuelve la respuesta automática según el cuestionario.
    """
    try:
        respuesta = obtener_respuesta_automatica(texto_usuario)
        return respuesta
    except Exception as e:
        print(f"❌ Error en procesar_mensaje: {e}")
        return "Lo siento, no entendí tu mensaje. ¿Podrías repetirlo?"
