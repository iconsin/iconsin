
import os, json
from sqlalchemy import create_engine, text

class StateStore:
    def __init__(self, database_url: str = "sqlite:///data/bot.db"):
        self.database_url = database_url
        os.makedirs("data", exist_ok=True)
        self.engine = create_engine(self.database_url, future=True)
        self._init_db()

    def _init_db(self):
        with self.engine.begin() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS flows (
                user_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL
            );
            """))
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                name TEXT,
                need TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """))

    def get_flow(self, user_id: str):
        with self.engine.begin() as conn:
            row = conn.execute(text("SELECT state_json FROM flows WHERE user_id=:u"), {"u": user_id}).fetchone()
            return json.loads(row[0]) if row else None

    def set_flow(self, user_id: str, state: dict):
        s = json.dumps(state, ensure_ascii=False)
        with self.engine.begin() as conn:
            conn.execute(text("""
            INSERT INTO flows(user_id, state_json) VALUES(:u, :s)
            ON CONFLICT(user_id) DO UPDATE SET state_json=excluded.state_json
            """), {"u": user_id, "s": s})

    def clear_flow(self, user_id: str):
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM flows WHERE user_id=:u"), {"u": user_id})

    def save_lead(self, user_id: str, answers: dict):
        with self.engine.begin() as conn:
            conn.execute(text("""
            INSERT INTO leads(user_id, name, need, phone)
            VALUES(:u, :n, :d, :p)
            """), {
                "u": user_id,
                "n": answers.get("name"),
                "d": answers.get("need"),
                "p": answers.get("phone")
            })
