import customtkinter as ctk
import sqlite3
import google.generativeai as genai
from datetime import datetime


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
class DatabaseManager:
    def __init__(self, db_nomi="repetitor.db"):
        self.ulanish = sqlite3.connect(db_nomi)
        self._jadval_yaratish()

    def _jadval_yaratish(self):
        self.ulanish.execute("""
            CREATE TABLE IF NOT EXISTS tahlillar (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                xato  TEXT,
                kod   TEXT,
                vaqt  TEXT
            )
        """)
        self.ulanish.commit()

    def saqlash(self, xato: str, kod: str):
        self.ulanish.execute(
            "INSERT INTO tahlillar (xato, kod, vaqt) VALUES (?, ?, ?)",
            (xato, kod, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.ulanish.commit()

    def tarix(self, limit=20):
        cur = self.ulanish.execute(
            "SELECT vaqt, xato, kod FROM tahlillar ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cur.fetchall()

    def yopish(self):
        self.ulanish.close()


# ─────────────────────────────────────────────
# AI CONTROLLER
# ─────────────────────────────────────────────
class AIController:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def tahlil_va_maslahat(self, kod: str, xato: str) -> str:
        prompt = f"""
Sen Python o'qituvchisi (repetitor)siz.
Quyidagi Python kodini va xatoni tahlil qilib,
o'zbek tilida oddiy va tushunarli tushuntirish bering.

--- KOD ---
{kod.strip()}

--- XATO ---
{xato.strip()}

Iltimos:
1. Xato nima sababdan chiqdi — oddiy so'z bilan tushuntiring.
2. To'g'ri kod variantini ko'rsating.
3. Bunday xatoga yo'l qo'ymaslik uchun maslahat bering.
"""
        try:
            javob = self.model.generate_content(prompt)
            return javob.text
        except Exception as e:
            return f"[Xatolik] Gemini javob bermadi:\n{e}"


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI REPETITOR - MAGISTRALIK ISHI")
        self.geometry("850x650")

        self.db = DatabaseManager()
        self.ai = None

        ctk.CTkLabel(self, text="PYTHON TAHLIL TIZIMI", font=("Arial", 24)).pack(pady=20)

        self.kod_input = ctk.CTkTextbox(self, width=750, height=200)
        self.kod_input.pack(pady=10)

        ctk.CTkButton(self, text="TAHLIL QILISH", command=self.ishlash).pack(pady=15)

        self.javob_output = ctk.CTkTextbox(self, width=750, height=200)
        self.javob_output.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.yopish)

    def xato_ushlash(self, kod: str) -> str:
        try:
            compile(kod, "<string>", "exec")
            return "Xato topilmadi"
        except SyntaxError as e:
            return f"SyntaxError: {e.msg} (qator {e.lineno})"
        except Exception as e:
            return str(e)

    def ishlash(self):
        if not self.ai:
            key = ctk.CTkInputDialog(text="Gemini API Key:", title="Kirish").get_input()
            if key:
                try:
                    self.ai = AIController(key)
                except Exception as e:
                    self.ai = None
                    self.javob_output.delete("1.0", "end")
                    self.javob_output.insert("1.0", f"API Key xato:\n{e}")
                    return
            else:
                return

        kod = self.kod_input.get("1.0", "end")
        xato = self.xato_ushlash(kod)

        javob = self.ai.tahlil_va_maslahat(kod, xato)
        self.db.saqlash(xato, kod)

        self.javob_output.delete("1.0", "end")
        self.javob_output.insert("1.0", javob)

    def yopish(self):
        self.db.yopish()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
