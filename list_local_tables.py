import sqlite3
import os

db_path = 'hyper_sync.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tabelas encontradas:")
    for table in tables:
        print(f"- {table[0]}")
    conn.close()
else:
    print("Banco de dados local 'hyper_sync.db' não encontrado.")
