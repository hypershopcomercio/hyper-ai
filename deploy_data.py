import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os

# CONFIGURAÇÕES DO SERVIDOR (PRODUÇÃO)
DB_USER = "root"
DB_PASS = "gWh28@@dGcMp"
DB_HOST = "187.127.253.245"
DB_NAME = "hyper_sync"
MYSQL_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# CONFIGURAÇÃO LOCAL
SQLITE_PATH = "hyper_sync.db"

def migrate():
    print(f"--- Iniciando Migração: {SQLITE_PATH} -> MySQL ---")
    
    if not os.path.exists(SQLITE_PATH):
        print(f"Erro: Arquivo {SQLITE_PATH} não encontrado localmente.")
        return

    # Conectar ao SQLite
    local_conn = sqlite3.connect(SQLITE_PATH)
    local_conn.row_factory = sqlite3.Row
    local_cursor = local_conn.cursor()

    # Conectar ao MySQL
    try:
        remote_engine = create_engine(MYSQL_URL)
        RemoteSession = sessionmaker(bind=remote_engine)
        remote_session = RemoteSession()
        print("Conectado ao MySQL com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar no MySQL: {e}")
        return

    # Tabelas para migrar (na ordem correta de dependência)
    tables = [
        "tokens", "oauth_tokens", "tiny_products", "ads", "sales", 
        "metrics", "ad_tiny_links", "system_config"
    ]

    for table in tables:
        print(f"Migrando tabela: {table}...", end=" ", flush=True)
        try:
            # Ler dados do SQLite
            local_cursor.execute(f"SELECT * FROM {table}")
            rows = local_cursor.fetchall()
            
            if not rows:
                print("Vazia. Pulando.")
                continue

            # Converter para lista de dicionários
            data = [dict(row) for row in rows]
            
            # Inserir no MySQL (usando SQLAlchemy Core para performance)
            meta = MetaData()
            meta.reflect(bind=remote_engine)
            target_table = meta.tables.get(table)
            
            if target_table is not None:
                # Limpar tabela antes (opcional, para evitar duplicados)
                # remote_engine.execute(target_table.delete()) 
                
                remote_engine.execute(target_table.insert(), data)
                print(f"OK ({len(data)} registros)")
            else:
                print(f"Erro: Tabela {table} não encontrada no banco MySQL.")
                
        except Exception as e:
            print(f"ERRO: {e}")

    local_conn.close()
    remote_session.close()
    print("\n--- Migração Concluída! ---")

if __name__ == "__main__":
    migrate()
