PREGUNTAS = {
    "rrhh": {
        "horario laboral": "El horario laboral es de lunes a viernes, de 8:00 a.m. a 5:00 p.m.",
        "vacaciones": "Las vacaciones deben solicitarse con al menos 15 días de antelación.",
        "permiso": "Para permisos especiales, escribe a rrhh@iconsanet.com."
    },
    "contabilidad": {
        "factura": "Las facturas se emiten los días 15 y 30 de cada mes.",
        "viático": "Los viáticos deben solicitarse con aprobación previa de la gerencia."
    },
    "calidad": {
        "iso": "El sistema de gestión ISO 9001 se audita anualmente.",
        "no conformidad": "Debes registrar la no conformidad en el formulario interno QMS-05."
    }
}

def buscar_respuesta(texto):
    texto = (texto or "").lower()
    for area, preguntas in PREGUNTAS.items():
        for clave, respuesta in preguntas.items():
            if clave in texto:
                return f"[{area.upper()}] {respuesta}"
    return None
