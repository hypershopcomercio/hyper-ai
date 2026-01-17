from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("Tentando adicionar coluna original_price na tabela competitor_ads...")
    db.execute(text("ALTER TABLE competitor_ads ADD COLUMN original_price FLOAT"))
    db.commit()
    print("✅ Coluna 'original_price' adicionada com sucesso!")
except Exception as e:
    print(f"⚠️  Nota: {e}")
    # Se já existir, tudo bem.
    
db.close()
