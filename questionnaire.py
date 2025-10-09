from typing import Optional
from state_store import StateStore

STEPS = [
    {"key": "name", "q": "¡Hola! Soy el asistente virtual de atención. ¿Podrías decirme tu nombre?"},
    {"key": "need", "q": "¿Podrías indicarme brevemente en qué necesitas ayuda hoy?"},
    {"key": "phone", "q": "¿Me compartes tu número de teléfono para que un asesor te contacte?"},
]

FINAL_MSG = (
    "Gracias, registré tus datos. Un asesor de ICONSA te contactará pronto. "
    "Puedes escribir 'FIN' para cerrar el registro o continuar con otra consulta."
)

class Questionnaire:
    def __init__(self, store: StateStore):
        self.store = store

    def handle_message(self, user_id: str, message: str) -> Optional[str]:
        if not message:
            return None
        if message.upper() in {"CANCEL", "SALIR"}:
            self.store.clear_flow(user_id)
            return "Cuestionario cancelado. ¿Hay algo más en lo que pueda asistirte?"

        state = self.store.get_flow(user_id) or {"step_idx": 0, "answers": {}}
        if state.get("completed"):
            if message.upper() == "FIN":
                self.store.clear_flow(user_id)
                return "Proceso finalizado. ¡Gracias por contactarnos!"
            return None

        step_idx = state.get("step_idx", 0)
        answers = state.get("answers", {})

        answers[STEPS[step_idx]["key"]] = message.strip()
        step_idx += 1

        if step_idx >= len(STEPS):
            self.store.save_lead(user_id, answers)
            self.store.set_flow(user_id, {"completed": True, "answers": answers})
            return FINAL_MSG
        else:
            self.store.set_flow(user_id, {"step_idx": step_idx, "answers": answers})
            return STEPS[step_idx]["q"]
