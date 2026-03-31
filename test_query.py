from database_manager import DatabaseManager
import datetime

db = DatabaseManager('estoque.db')
db.connect()

results = db.get_stock_entries()
print(f"Resultados: {len(results)}")
if results:
    for row in results:
        print(dict(row))
        
import sys
from CTkTable import CTkTable
import customtkinter as ctk

app = ctk.CTk()
frame = ctk.CTkFrame(app)
frame.pack()
table = CTkTable(master=frame, values=[["A", "B"], ["1", "2"]])
table.pack()
print(hasattr(table, 'update_values'))

sys.exit(0)
