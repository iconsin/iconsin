# questionnaire.py
def obtener_respuesta_automatica(mensaje: str) -> str:
    """
    Retorna una respuesta automática básica según el mensaje del usuario.
    Esta versión no usa IA, solo reglas simples.
    """

    mensaje = mensaje.lower().strip()

    if any(palabra in mensaje for palabra in ["hola", "buenas", "saludo"]):
        return "¡Hola! 👋 Soy el asistente virtual de ICONSA. ¿En qué puedo ayudarte?"

    if "documento" in mensaje or "contrato" in mensaje or "factura" in mensaje:
        return "¿Podrías indicarme el nombre o tipo de documento que necesitas?"

    if "gracias" in mensaje:
        return "¡Con gusto! 😊 Si necesitas algo más, estoy aquí para ayudarte."

    # Respuesta por defecto
    return "Estoy aquí para ayudarte. ¿Podrías especificar tu consulta?"
