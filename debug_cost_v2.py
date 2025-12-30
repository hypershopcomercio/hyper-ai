from app.core.database import SessionLocal
from app.models.tiny_product import TinyProduct

db = SessionLocal()

print("--- FINAL CHECK ---")
siblings = db.query(TinyProduct).filter(TinyProduct.sku.ilike('KIT-CUIDADOS%')).all()
for s in siblings:
    print(f"SKU: {s.sku} | Cost: {s.cost}")

db.close()
