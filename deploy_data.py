import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, MetaData
import os
import urllib.parse

# CONFIGURAÇÕES DO SERVIDOR (PRODUÇÃO)
DB_USER = "root"
DB_PASS = "gWh28@@dGcMp"  # Senha com @
DB_HOST = "187.127.253.245"
DB_NAME = "hyper_sync"

# CODIFICAR A SENHA PARA NÃO DAR ERRO NO @
encoded_pass = urllib.parse.quote_plus(DB_PASS)
MYSQL_URL = f"mysql+pymysql://{DB_USER}:{encoded_pass}@{DB_HOST}/{DB_NAME}"

# CONFIGURAÇÃO LOCAL
SQLITE_PATH = "hyper_sync.db"

def migrate():
    print(f"--- Iniciando Migração Completa: {SQLITE_PATH} -> MySQL ---")
    
    if not os.path.exists(SQLITE_PATH):
        print(f"Erro: Arquivo {SQLITE_PATH} não encontrado localmente.")
        return

    local_conn = sqlite3.connect(SQLITE_PATH)
    local_conn.row_factory = sqlite3.Row
    local_cursor = local_conn.cursor()

    try:
        remote_engine = create_engine(MYSQL_URL)
        with remote_engine.connect() as conn:
            conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 0;"))
            print("Conectado ao MySQL e verificações de integridade desativadas temporariamente.")
    except Exception as e:
        print(f"Erro ao conectar no MySQL: {e}")
        return

    # LISTA COMPLETA DE TABELAS
    local_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in local_cursor.fetchall()]

    for table in tables:
        print(f"Migrando tabela: {table}...", end=" ", flush=True)
        try:
            local_cursor.execute(f"SELECT * FROM {table}")
            rows = local_cursor.fetchall()
            
            if not rows:
                print("Vazia. Pulando.")
                continue

            data = [dict(row) for row in rows]
            meta = MetaData()
            meta.reflect(bind=remote_engine)
            target_table = meta.tables.get(table)
            
            if target_table is not None:
                with remote_engine.connect() as conn:
                    # Usar o text() do SQLAlchemy para comandos diretos
                    conn.execute(target_table.delete())
                    conn.execute(target_table.insert(), data)
                    conn.commit()
                print(f"OK ({len(data)} registros)")
            else:
                print(f"Ignorada (Não existe no destino)")
                
        except Exception as e:
            print(f"ERRO: {e}")

    # Reativar FK Checks
    with remote_engine.connect() as conn:
        conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 1;"))

    local_conn.close()
    print("\n--- Migração Total Concluída! ---")
    print("Agora você já pode logar no sistema com adm@hypershop.com")

if __name__ == "__main__":
    migrate()
