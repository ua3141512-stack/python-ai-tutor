import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # Bazaga ulanish
        self.conn = sqlite3.connect("magistr_tizim.db", check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        # Dissertatsiya statistikasi uchun yagona jadval
        cursor.execute('''CREATE TABLE IF NOT EXISTS xatolar_logi 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           xato_turi TEXT, kod TEXT, vaqt DATETIME)''')
        self.conn.commit()

    def saqlash(self, xato, kod):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO xatolar_logi (xato_turi, kod, vaqt) VALUES (?, ?, ?)", 
                       (xato, kod, datetime.now()))
        self.conn.commit()