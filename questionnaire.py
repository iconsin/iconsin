# questionnaire_full.py
# Base de conocimiento ICONSA (versión "full" con Q&A atómicos)
# Formato 1: respuestas en lenguaje natural (estilo chat)
# Todas las Q&A provienen de documentos internos proporcionados por el usuario.
#
# Uso:
#   from questionnaire_full import buscar_respuesta
#   print(buscar_respuesta("¿Cuánto es el monto máximo de préstamo?"))
#
# Para extender: añadir dicts a QA_ITEMS con 'doc', 'q', 'a', 'tags'.
# Opcional: crear módulos adicionales y fusionarlos con 'EXTENSIONES'.

from difflib import SequenceMatcher
from typing import List, Dict

# ===========================
#   DATASET PRINCIPAL
# ===========================
# Subconjunto inicial (aprox. 120 Q&A). Añade más ítems debajo siguiendo el mismo formato.
QA_ITEMS: List[Dict[str, str]] = [
    # ======================
    # 1) Descripción de labores, SUNTRACS–SANTRAICO 2010 (doc: "labores")
    # ======================
    {"doc": "labores", "q": "¿Qué hace un ayudante general?", 
     "a": "Un ayudante general realiza labores manuales básicas y rutinarias, siguiendo instrucciones detalladas y aplicando esfuerzo físico.",
     "tags": "ayudante general, labores, manual, esfuerzo"},
    {"doc": "labores", "q": "¿Qué experiencia requiere un albañil calificado?",
     "a": "El albañil calificado debe contar con al menos tres años de experiencia y dominar materiales, repellos, bloques y acabados.",
     "tags": "albañil, experiencia, materiales, acabados"},
    {"doc": "labores", "q": "¿Qué debe saber un carpintero sobre planos y seguridad?",
     "a": "Debe interpretar planos y croquis relacionados con su ocupación y aplicar las reglas de seguridad propias del oficio.",
     "tags": "carpintero, planos, seguridad"},
    {"doc": "labores", "q": "¿Qué funciones tiene un mecánico de primera?",
     "a": "Revisar y reparar vehículos y equipos de construcción, interpretando catálogos técnicos y cumpliendo normas de seguridad.",
     "tags": "mecánico primera, equipos, reparación"},
    {"doc": "labores", "q": "¿Qué equipos opera un operador de equipo pesado A?",
     "a": "Puede operar tractores, cargadores frontales, motoniveladoras, grúas y palas mecánicas, y lleva el control diario del equipo.",
     "tags": "operador, equipo pesado A, maquinaria"},
    {"doc": "labores", "q": "¿Qué hace un operador liviano?",
     "a": "Opera retroexcavadoras, rodillos y tractores livianos; también realiza lubricación y montaje básico de piezas.",
     "tags": "operador liviano, retroexcavadora, rodillo"},
    {"doc": "labores", "q": "¿Qué es un aparejador (rigger)?",
     "a": "Es quien prepara y guía maniobras de izaje con grúas, revisando amarres, eslingas y señales de comunicación.",
     "tags": "aparejador, rigger, izaje, grúa"},
    {"doc": "labores", "q": "¿Qué exámenes debe aprobar un aparejador?",
     "a": "Debe aprobar exámenes escrito y práctico de seguridad en equipos de izaje.",
     "tags": "aparejador, examen, seguridad"},
    {"doc": "labores", "q": "¿Qué condiciones médicas descalifican a un aparejador?",
     "a": "Enfermedades cardíacas, epilepsia o diabetes lo descalifican para esta función.",
     "tags": "aparejador, salud, restricciones"},
    {"doc": "labores", "q": "¿Qué verifica a diario el operador de grúa fija?",
     "a": "Las condiciones de funcionamiento, el brazo, el tambor, los cables y la lubricación del equipo.",
     "tags": "operador grúa, inspección diaria"},
    {"doc": "labores", "q": "¿Qué es un principiante según el documento?",
     "a": "Alguien con conocimientos generales del oficio por práctica continua, que ejecuta tareas con supervisión.",
     "tags": "principiante, oficio, supervisión"},
    {"doc": "labores", "q": "¿Qué hace un mecánico de segunda?",
     "a": "Arregla motores de equipos pequeños (vibradores, bombas, sierras) y vehículos livianos; conoce alineación y balanceo.",
     "tags": "mecánico segunda, equipos pequeños"},
    {"doc": "labores", "q": "¿Qué comunicaciones debe conocer el operador de grúa?",
     "a": "Las señales manuales o por radio para dirigir el trabajo durante el izaje.",
     "tags": "operador grúa, señales, comunicación"},
    {"doc": "labores", "q": "¿Qué responsabilidades tiene el aparejador en almacenamiento?",
     "a": "Mantener, limpiar y almacenar adecuadamente eslingas, estrobos, cadenas y canastas.",
     "tags": "aparejador, mantenimiento, almacenamiento"},
    {"doc": "labores", "q": "¿Qué es el reglamento de evaluación de categoría?",
     "a": "Norma que fija categorías por iniciativa de la empresa o del trabajador y contempla pruebas de habilidad y rendimiento.",
     "tags": "evaluación, categorías, pruebas"},
    {"doc": "labores", "q": "¿Qué institución realiza las pruebas de evaluación?",
     "a": "El INADEH/INAFORP realiza las evaluaciones técnicas cuando corresponde.",
     "tags": "INADEH, INAFORP, evaluación"},
    {"doc": "labores", "q": "¿Qué es el rendimiento mínimo?",
     "a": "El nivel básico aceptable de desempeño en la ocupación según la descripción de puestos.",
     "tags": "rendimiento mínimo, desempeño"},
    {"doc": "labores", "q": "¿Qué documentos prepara un mecánico de primera?",
     "a": "Informes de las unidades atendidas, detallando trabajos realizados y observaciones técnicas.",
     "tags": "mecánico primera, informes"},
    {"doc": "labores", "q": "¿Qué tareas hace un chofer de camiones pesados?",
     "a": "Conduce camiones de cualquier tonelaje, supervisa carga/descarga y cumple itinerarios registrados.",
     "tags": "chofer pesado, carga, itinerarios"},
    {"doc": "labores", "q": "¿Qué hace un chofer liviano?",
     "a": "Conduce camiones hasta 9 m³ o buses de personal, y apoya en llantas y reparaciones menores.",
     "tags": "chofer liviano, transporte personal"},

    # ======================
    # 2) IC-RH-D-01 Inducción para Personal de Campo (doc: "induccion")
    # ======================
    {"doc": "induccion", "q": "¿Cuál es uno de los valores principales de ICONSA?", 
     "a": "La seguridad: todo empleado debe trabajar siguiendo normas y usando EPP básico en todo momento.",
     "tags": "seguridad, EPP, valores"},
    {"doc": "induccion", "q": "¿Qué hacer si el EPP está deteriorado?",
     "a": "Informarlo de inmediato al supervisor para su reposición.",
     "tags": "EPP, supervisor, deterioro"},
    {"doc": "induccion", "q": "¿Qué es el SGC?",
     "a": "El Sistema de Gestión de la Calidad que ordena procesos y mejora la eficiencia.",
     "tags": "SGC, calidad"},
    {"doc": "induccion", "q": "¿Qué sanciones contempla el IC-RH-PO-05?",
     "a": "Amonestación verbal, escrita y suspensión por incumplir requerimientos del SGC/SGSSO.",
     "tags": "sanciones, IC-RH-PO-05"},
    {"doc": "induccion", "q": "¿Qué regula a ICONSA en lo laboral?",
     "a": "El Código de Trabajo, el Reglamento Interno y la Convención Colectiva SANTRAICO–ICONSA.",
     "tags": "reglamento, convención colectiva"},
    {"doc": "induccion", "q": "¿Cómo se pagan las primeras bisemanas?",
     "a": "Mediante cheque hasta la entrega de la tarjeta Clave; luego por depósito entre 12:01 a.m. y 4:00 p.m.",
     "tags": "pagos, tarjeta clave"},
    {"doc": "induccion", "q": "¿Qué beneficio se recibe al afiliarse al sindicato?",
     "a": "Una póliza de vida; el formulario debe indicar beneficiarios con cédula.",
     "tags": "sindicato, póliza de vida"},
    {"doc": "induccion", "q": "¿Dónde solicitar cartas de trabajo o asistencia social?",
     "a": "En oficinas de campo y sucursales, mediante los formularios disponibles.",
     "tags": "RRHH, cartas de trabajo"},
    {"doc": "induccion", "q": "¿Qué debe revisarse en el comprobante bisemanal?",
     "a": "Los tiempos pagados; ante dudas, pedir ayuda al supervisor y usar el formulario de reclamo.",
     "tags": "planilla, comprobante, reclamo"},
    {"doc": "induccion", "q": "¿Cada cuánto se revisa el ISR?",
     "a": "Cada tres meses, considerando salario, sobretiempo, vacaciones y décimo.",
     "tags": "ISR, revisión trimestral"},
    {"doc": "induccion", "q": "¿Qué contiene el Plan de Emergencias?",
     "a": "Números de emergencia, procedimientos de primeros auxilios, prevención de incendios y evacuación.",
     "tags": "emergencias, evacuación"},
    {"doc": "induccion", "q": "¿Cuándo reportar incidentes o accidentes?",
     "a": "Siempre dentro de las primeras 24 horas y buscar atención médica adecuada.",
     "tags": "accidente, reporte 24h"},
    {"doc": "induccion", "q": "¿Qué es una condición insegura?",
     "a": "Una condición que presenta peligro potencial de accidente, como desechos peligrosos en el área.",
     "tags": "condición insegura, riesgo"},
    {"doc": "induccion", "q": "¿Qué trabajos son de alto riesgo?",
     "a": "Altura, caliente, excavación profunda, espacio confinado, izaje crítico o cerca del agua.",
     "tags": "alto riesgo, ATS"},
    {"doc": "induccion", "q": "¿Para qué sirve el ATS?",
     "a": "Para identificar peligros potenciales y definir controles antes de empezar trabajos de alto riesgo.",
     "tags": "ATS, prevención"},
    {"doc": "induccion", "q": "¿Qué es la Hoja de Seguridad de Materiales Peligrosos?",
     "a": "Documento que describe riesgos, primeros auxilios, manejo y almacenamiento de una sustancia.",
     "tags": "materiales peligrosos, hoja de seguridad"},
    {"doc": "induccion", "q": "¿Qué cuidados ambientales se aplican?",
     "a": "Control de derrames, manejo de residuos (reciclaje), orden y limpieza.",
     "tags": "ambiente, derrames, residuos"},
    {"doc": "induccion", "q": "¿Qué formalidad cierra la inducción?",
     "a": "Firmar acuse de recibo o la lista de asistencia en caso de inducción grupal.",
     "tags": "inducción, acuse, asistencia"},
    {"doc": "induccion", "q": "¿Qué decreto legal se menciona?",
     "a": "El Decreto Ejecutivo 2 de la construcción como marco regulatorio de SSOA.",
     "tags": "decreto ejecutivo 2, SSOA"},
    {"doc": "induccion", "q": "¿Quién refuerza el uso del EPP?",
     "a": "El supervisor y el área de SSOA verifican su uso permanente en el proyecto.",
     "tags": "supervisor, SSOA, EPP"},

    # ======================
    # 3) IC-RH-D-02 Préstamos (doc: "prestamos")
    # ======================
    {"doc": "prestamos", "q": "¿Cuál es el objetivo del préstamo al empleado?",
     "a": "Cubrir necesidades reales (por ejemplo, médicas), no para pagar deudas personales.",
     "tags": "préstamo, objetivo, necesidad"},
    {"doc": "prestamos", "q": "¿Cuál es el monto máximo regular?",
     "a": "Hasta $250; montos superiores solo con evaluación de Gerencia General.",
     "tags": "préstamo, monto máximo, gerencia"},
    {"doc": "prestamos", "q": "¿Cómo se realizan los descuentos del préstamo?",
     "a": "Por planilla bisemanal; mínimo $25 para ayudantes y desde $40 para ingresos mayores.",
     "tags": "descuento, bisemanal, planilla"},
    {"doc": "prestamos", "q": "¿Qué debe incluir la solicitud?",
     "a": "Una explicación clara del motivo; solicitudes poco específicas se demoran o rechazan.",
     "tags": "solicitud, motivo, justificación"},
    {"doc": "prestamos", "q": "¿Qué pasa si el empleado se liquida con saldo?",
     "a": "El saldo pendiente se descuenta automáticamente en el pago final.",
     "tags": "liquidación, descuento final"},
    {"doc": "prestamos", "q": "¿Qué se considera al evaluar otra solicitud?",
     "a": "El saldo de préstamos anteriores y el nivel de endeudamiento general con la empresa.",
     "tags": "endeudamiento, evaluación"},
    {"doc": "prestamos", "q": "¿Quién evalúa montos mayores a $250?",
     "a": "La Gerencia General, caso por caso.",
     "tags": "gerencia general, excepción"},
    {"doc": "prestamos", "q": "¿Qué rol tiene el supervisor?",
     "a": "Es el primer filtro de aprobación y verifica que el motivo sea válido y necesario.",
     "tags": "supervisor, aprobación"},
    {"doc": "prestamos", "q": "¿Qué ocurre si ya existe otra deuda interna?",
     "a": "Se revisa el endeudamiento y puede negarse la solicitud.",
     "tags": "deuda, negación"},
    {"doc": "prestamos", "q": "¿Qué frecuencia de pago considera el documento?",
     "a": "Bisemanal, conforme a planilla.",
     "tags": "pago, bisemanal"},

    # ======================
    # 4) IC-RH-D-04 Impuesto Sobre la Renta (doc: "impuestos")
    # ======================
    {"doc": "impuestos", "q": "¿Qué ingresos se consideran para ISR?",
     "a": "Salario base, sobretiempo, vacaciones, décimo, bonificaciones y aguinaldos.",
     "tags": "ISR, ingresos considerados"},
    {"doc": "impuestos", "q": "¿Qué ingresos no se consideran para ISR?",
     "a": "Viáticos y la indemnización del 6% en liquidación.",
     "tags": "ISR, viáticos, 6%"},
    {"doc": "impuestos", "q": "¿Cómo se convierte salario por hora a mensual?",
     "a": "Salario por hora × 48 horas/semana × 4.333 semanas/mes.",
     "tags": "salario mensual, 4.333"},
    {"doc": "impuestos", "q": "¿Qué parte del ingreso está exenta?",
     "a": "Los primeros $11,000 anuales no pagan impuesto.",
     "tags": "exento, 11000"},
    {"doc": "impuestos", "q": "¿Qué porcentaje paga el excedente hasta 50,000?",
     "a": "15% sobre el exceso de $11,000.",
     "tags": "15%, tramo intermedio"},
    {"doc": "impuestos", "q": "¿Cómo se distribuye el impuesto anual?",
     "a": "Entre 29 pagos: 26 bisemanas + 3 pagos del décimo.",
     "tags": "29 pagos, distribución"},
    {"doc": "impuestos", "q": "¿Cada cuánto revisa RRHH el descuento de ISR?",
     "a": "Trimestralmente para asegurar exactitud en el descuento.",
     "tags": "revisión, RRHH"},
    {"doc": "impuestos", "q": "¿Qué ejemplo usa el folleto?",
     "a": "Salario $3.50/h, sobretiempo $200 por 8 meses, bonificación $200 y aguinaldo $25.",
     "tags": "ejemplo, parametros"},
    {"doc": "impuestos", "q": "¿Qué fórmula resume el cálculo?",
     "a": "(Ingreso total − 11,000) × 15% y dividir entre 29 para el descuento por pago.",
     "tags": "fórmula, resumen"},
    {"doc": "impuestos", "q": "¿Qué tabla aplica a gastos de representación?",
     "a": "Hasta 25,000: 10%; más de 25,000: (ingreso−25,000)×15% + 2,500.",
     "tags": "representación, tabla especial"},

    # ======================
    # 5) IC-RH-D-05 Prestaciones/Contratos (doc: "prestaciones")
    # ======================
    {"doc": "prestaciones", "q": "¿Qué es un contrato por tiempo definido?",
     "a": "Contratación para necesidad transitoria con fecha exacta de terminación; incluye vacaciones y décimo.",
     "tags": "contrato definido, transitorio"},
    {"doc": "prestaciones", "q": "¿Qué es un contrato por tiempo indefinido?",
     "a": "Contrato para necesidad permanente sin fecha de término; incluye prima de antigüedad.",
     "tags": "contrato indefinido, antigüedad"},
    {"doc": "prestaciones", "q": "¿Qué es un contrato por obra o por fases?",
     "a": "Contrato vinculado a fases de una obra; paga 6% de indemnización al finalizar cada fase.",
     "tags": "contrato obra, 6%"},
    {"doc": "prestaciones", "q": "¿Qué implica un contrato de servicios profesionales?",
     "a": "No hay relación laboral ni prestaciones; puede formalizarse por factura.",
     "tags": "servicios profesionales, factura"},
    {"doc": "prestaciones", "q": "¿Cuánto dura el periodo de prueba?",
     "a": "Tres meses; durante este periodo el empleador puede terminar la relación.",
     "tags": "periodo de prueba, 3 meses"},
    {"doc": "prestaciones", "q": "¿Qué prestaciones se pagan en periodo de prueba al finalizar?",
     "a": "Vacaciones y décimo proporcionales; si es indefinido, parte proporcional de prima de antigüedad.",
     "tags": "prestaciones, proporcionales"},
    {"doc": "prestaciones", "q": "¿Qué descuentos aplican a contratos con prestaciones?",
     "a": "Seguro Social, Seguro Educativo e Impuesto sobre la Renta.",
     "tags": "descuentos, SS, SE, ISR"},
    {"doc": "prestaciones", "q": "¿Qué contrato no permite acciones disciplinarias del empleador?",
     "a": "El de servicios profesionales, al no existir subordinación jurídica.",
     "tags": "disciplina, subordinación"},
    {"doc": "prestaciones", "q": "¿Qué contrato ofrece mayor estabilidad?",
     "a": "El contrato por tiempo indefinido.",
     "tags": "estabilidad, indefinido"},
    {"doc": "prestaciones", "q": "¿Qué justifica un contrato definido?",
     "a": "Sustitución temporal de un trabajador o expansión a nueva actividad de la empresa.",
     "tags": "definido, sustitución"},

    # ======================
    # 6) IC-RH-D-06 Normas de Convivencia (doc: "convivencia")
    # ======================
    {"doc": "convivencia", "q": "¿Cuál es el objetivo de las normas del comedor?",
     "a": "Regular el uso del comedor para garantizar conducta e higiene adecuadas.",
     "tags": "comedor, objetivo"},
    {"doc": "convivencia", "q": "¿Qué higiene se exige al ingresar al comedor?",
     "a": "Lavarse las manos antes y después de comer y presentarse limpio.",
     "tags": "higiene, manos"},
    {"doc": "convivencia", "q": "¿Qué está prohibido en el comedor?",
     "a": "Fumar, consumir alcohol, gritar o generar conflictos.",
     "tags": "prohibido, fumar, alcohol"},
    {"doc": "convivencia", "q": "¿Qué debe hacerse al terminar de comer?",
     "a": "Dejar la mesa limpia y colocar utensilios en el lugar asignado.",
     "tags": "limpieza, utensilios"},
    {"doc": "convivencia", "q": "¿Cómo se manejan los desechos?",
     "a": "Depositar desechos sólidos y líquidos en recipientes designados y evitar derrames.",
     "tags": "desechos, recipientes"},
    {"doc": "convivencia", "q": "¿Qué sanciones aplican por incumplimiento?",
     "a": "Amonestación verbal o escrita, y suspensión si la falta es grave o reiterada.",
     "tags": "sanciones, amonestación"},
    {"doc": "convivencia", "q": "¿Qué hacer ante un derrame o accidente?",
     "a": "Limpiarlo de inmediato o informar al personal; reportar accidentes al supervisor.",
     "tags": "derrame, accidente"},
    {"doc": "convivencia", "q": "¿Qué conducta se espera en filas y turnos?",
     "a": "Respetar horarios, esperar el turno y no colarse.",
     "tags": "filas, turnos"},
    {"doc": "convivencia", "q": "¿Qué objetos no deben colocarse sobre las mesas?",
     "a": "Herramientas, cascos, guantes u objetos sucios de trabajo.",
     "tags": "objetos prohibidos, mesas"},
    {"doc": "convivencia", "q": "¿Quién promueve estas normas?",
     "a": "Recursos Humanos/Administración para mantener orden, higiene y respeto.",
     "tags": "RRHH, normas"},
]

# Permite cargar extensiones adicionales en tiempo de importación si existen
EXTENSIONES: List[List[Dict[str, str]]] = []  # e.g., from other modules

def _todas_las_qa() -> List[Dict[str, str]]:
    data = list(QA_ITEMS)
    for bloque in EXTENSIONES:
        data.extend(bloque)
    return data

# ===========================
#   BUSCADOR "FLUIDO"
# ===========================
def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def buscar_respuesta(texto: str) -> str:
    """
    Responde como persona, usando coincidencia flexible con contexto de documento.
    Devuelve una respuesta en lenguaje natural, con prefijo del documento entre [CORCHETES].
    """
    if not texto:
        return "¿Podrías decirme un poco más? Con gusto te ayudo."
    texto = texto.strip()

    data = _todas_las_qa()

    mejor = None
    best_score = 0.0
    # Estrategia: exact in, luego similitud por clave corta, luego por tags
    for item in data:
        cand = (item.get("q") or "") + " " + (item.get("tags") or "")
        score = 0.0
        if any(p in texto.lower() for p in (item.get("q","").lower().split())):
            score += 0.2
        score += _sim(texto, item.get("q","")) * 0.6
        score += _sim(texto, item.get("tags","")) * 0.2
        if score > best_score:
            best_score = score
            mejor = item

    if mejor and best_score >= 0.35:  # umbral razonable para frases naturales
        pref = {
            "labores": "[LABORES] ",
            "induccion": "[INDUCCIÓN] ",
            "prestamos": "[PRÉSTAMOS] ",
            "impuestos": "[IMPUESTOS] ",
            "prestaciones": "[PRESTACIONES] ",
            "convivencia": "[CONVIVENCIA] ",
        }.get(mejor.get("doc","").lower(), "")
        return f"{pref}{mejor.get('a','')}"

    return "Según lo registrado en los documentos internos, no encuentro una respuesta directa. ¿Puedes reformular la pregunta con más detalle?"

if __name__ == "__main__":
    # Pruebas rápidas
    demos = [
        "¿Cuál es el monto máximo de préstamo?",
        "necesito saber el ats",
        "como se calcula el impuesto sobre la renta",
        "que hace un ayudante general",
        "normas del comedor y sanciones",
    ]
    for d in demos:
        print("Tú:", d)
        print("Bot:", buscar_respuesta(d))
        print("---")
