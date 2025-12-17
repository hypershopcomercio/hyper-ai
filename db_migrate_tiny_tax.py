
from app.core.database import engine, Base
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        with conn.begin():
            # Add columns if they don't exist
            try:
                conn.execute(text("ALTER TABLE tiny_products ADD COLUMN ncm VARCHAR"))
                print("Added ncm column")
            except Exception as e:
                print(f"Skipping ncm: {e}")
                
            try:
                conn.execute(text("ALTER TABLE tiny_products ADD COLUMN origin VARCHAR"))
                print("Added origin column")
            except Exception as e:
                print(f"Skipping origin: {e}")
                
            try:
                conn.execute(text("ALTER TABLE tiny_products ADD COLUMN supplier_name VARCHAR"))
                print("Added supplier_name column")
            except Exception as e:
                print(f"Skipping supplier_name: {e}")

if __name__ == "__main__":
    migrate()
