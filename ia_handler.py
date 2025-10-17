import json
from difflib import SequenceMatcher
import re

def load_knowledge_base():
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        return json.load(f)

def find_best_answer(user_input, knowledge_base, threshold=0.55):
    best_match = None
    best_score = 0
    for item in knowledge_base:
        score = SequenceMatcher(None, user_input.lower(), item["pregunta"].lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = item
    if best_score >= threshold and best_match:
        respuesta = best_match.get("respuesta", "")
        if re.search(r"https?://[^\s]+", respuesta or ""):
            return {"texto": respuesta, "tipo": "link", "departamento": best_match.get("departamento", "General")}
        return {"texto": respuesta, "tipo": "texto", "departamento": best_match.get("departamento", "General")}
    return {"texto": None, "tipo": "texto", "departamento": "General"}
