import sqlite3
import os

db_path = 'hyper_sync.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM users")
        users = cursor.fetchall()
        print("Usuários encontrados:")
        for user in users:
            print(f"- {user[0]}")
    except Exception as e:
        print(f"Erro ao ler tabela 'users': {e}")
    finally:
        conn.close()
else:
    print("Banco de dados local 'hyper_sync.db' não encontrado.")
