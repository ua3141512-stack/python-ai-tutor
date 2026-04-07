import customtkinter as ctk
from database_manager import DatabaseManager
from ai_controller import AIController

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
        
        self.javob_output = ctk.CTkTextbox(self, width=750, height=200, wrap="word")
        self.javob_output.pack(pady=10)

    def ishlash(self):
        if not self.ai:
            # Skrinshotdagi AIzaSy... bilan boshlanadigan kalitni kiriting
            key = ctk.CTkInputDialog(text="Gemini API Key:", title="Kirish").get_input()
            if key:
                self.ai = AIController(key)
            else:
                return

        kod = self.kod_input.get("1.0", "end")
        xato = "SyntaxError: invalid syntax" 
        
        javob = self.ai.tahlil_va_maslahat(kod, xato)
        self.db.saqlash(xato, kod)
        
        self.javob_output.delete("1.0", "end")
        self.javob_output.insert("1.0", javob)

if __name__ == "__main__":
    App().mainloop()