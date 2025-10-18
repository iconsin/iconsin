# questionnaire.py
# Asistente IC - Base de conocimiento institucional ICONSA
# Versión final con tono formal corporativo
# Autor: Jorge Torres

import difflib

SALUDO_INICIAL = "👋 Hola, soy Asistente IC. Estoy aquí para apoyarte con información de Recursos Humanos, Prestaciones, Seguridad y Normas internas."

BASE_DATOS = {
    "rrhh": {
        "descripcion": "Información general de Recursos Humanos.",
        "preguntas": {
            "vacaciones": "Las vacaciones deben solicitarse con al menos 15 días de antelación al Departamento de Recursos Humanos.",
            "permiso": "Los permisos especiales deben gestionarse mediante solicitud formal a Recursos Humanos.",
            "horario laboral": "El horario laboral regular es de lunes a viernes, de 8:00 a.m. a 5:00 p.m.",
            "correo rrhh": "Puede comunicarse con el Departamento de Recursos Humanos escribiendo a rrhh@iconsanet.com."
        }
    },
    "prestaciones": {
        "descripcion": "Información sobre beneficios y contratos laborales.",
        "preguntas": {
            "contrato definido": "Contrato de carácter temporal con fecha de término. Incluye vacaciones y décimo proporcional.",
            "contrato indefinido": "Contrato de carácter permanente que genera prima de antigüedad, vacaciones y décimo.",
            "periodo de prueba": "El periodo de prueba tiene una duración de tres meses, según el Código de Trabajo.",
            "indemnizacion": "La indemnización del 6% aplica en contratos por obra o fase, según lo establecido en la ley laboral panameña."
        }
    },
    "prestamos": {
        "descripcion": "Condiciones especiales para la solicitud de préstamos a empleados.",
        "preguntas": {
            "monto maximo": "El monto máximo de préstamo regular es de $250, salvo autorización especial de la Gerencia General.",
            "descuento": "Los descuentos se realizan por planilla bisemanal. El monto mínimo es de $25 por bisemana.",
            "liquidacion": "Si el empleado se liquida, el saldo pendiente del préstamo se descuenta automáticamente.",
            "evaluacion": "Antes de aprobar un préstamo, se evalúa el nivel de endeudamiento general del colaborador."
        }
    },
    "impuestos": {
        "descripcion": "Cálculo y aplicación del impuesto sobre la renta (ISR).",
        "preguntas": {
            "exento": "Los ingresos anuales hasta $11,000 están exentos de impuesto sobre la renta.",
            "porcentaje": "Los ingresos entre $11,001 y $50,000 pagan el 15% sobre el excedente de $11,000.",
            "descuento bisemanal": "El impuesto anual se divide entre 29 pagos (26 bisemanas y 3 décimos) para aplicar el descuento proporcional.",
            "revision": "Recursos Humanos revisa el descuento aplicado de ISR cada tres meses."
        }
    },
    "seguridad": {
        "descripcion": "Políticas y normas de seguridad e higiene en el trabajo.",
        "preguntas": {
            "ats": "El Análisis de Trabajo Seguro (ATS) identifica peligros y define controles antes de iniciar labores de alto riesgo.",
            "equipo de proteccion": "Todo empleado debe portar su equipo de protección personal en todo momento dentro del proyecto.",
            "accidente": "Cualquier accidente laboral debe reportarse a su supervisor y al área de Seguridad dentro de las primeras 24 horas.",
            "emergencia": "El plan de emergencias incluye primeros auxilios, prevención de incendios y procedimientos de evacuación."
        }
    },
    "convivencia": {
        "descripcion": "Reglamento de convivencia y conducta en el comedor institucional.",
        "preguntas": {
            "comedor": "El comedor debe mantenerse limpio, ordenado y en silencio. Está prohibido fumar o consumir bebidas alcohólicas.",
            "utensilios": "Cada trabajador debe devolver los utensilios y dejar el área de mesa limpia después de comer.",
            "respeto": "Se exige trato respetuoso y cordial hacia todos los compañeros y personal de cocina.",
            "sanciones": "Las faltas leves generan amonestaciones verbales; las graves pueden implicar suspensión temporal del uso del comedor."
        }
    },
    "general": {
        "descripcion": "Respuestas institucionales generales.",
        "preguntas": {
            "nombre": "Soy Asistente IC, el asistente institucional de ICONSA.",
            "presentacion": SALUDO_INICIAL,
            "saludo": SALUDO_INICIAL
        }
    }
}

ya_saludo = False

def buscar_respuesta(texto, inicio=False):
    global ya_saludo
    texto = (texto or "").lower().strip()

    if not ya_saludo or inicio:
        ya_saludo = True
        return SALUDO_INICIAL

    mejor_respuesta = None
    mayor_similitud = 0
    area_respuesta = None

    for area, datos in BASE_DATOS.items():
        for clave, respuesta in datos["preguntas"].items():
            similitud = difflib.SequenceMatcher(None, clave, texto).ratio()
            if clave in texto or similitud > 0.6:
                if similitud > mayor_similitud:
                    mayor_similitud = similitud
                    mejor_respuesta = respuesta
                    area_respuesta = area

    if mejor_respuesta:
        return f"[{area_respuesta.upper()}] {mejor_respuesta}"

    return ("No se encontró información exacta sobre ese tema en los documentos institucionales. "
            "Por favor, formule su consulta de manera más específica.")

if __name__ == "__main__":
    print(SALUDO_INICIAL)
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["salir", "exit", "q"]:
            break
        print("Asistente IC:", buscar_respuesta(pregunta))
