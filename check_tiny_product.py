
from app.core.database import SessionLocal
from app.models.tiny_product import TinyProduct

def check_db_tiny_product(sku):
    db = SessionLocal()
    tp = db.query(TinyProduct).filter(TinyProduct.sku == sku).first()
    if tp:
        print(f"Found TinyProduct in DB for SKU: {sku}")
        print(f"ID: {tp.id}")
        print(f"Name: {tp.name}")
        print(f"Cost: {tp.cost}")
        print(f"Updated At: {tp.updated_at}")
    else:
        print(f"TinyProduct NOT found in DB for SKU: {sku}")
    db.close()

if __name__ == "__main__":
    check_db_tiny_product("FECHADURA-VITRINE")
