
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.tiny_product import TinyProduct

SKU_TO_FIND = "ROUPAO-INFANTIL-MICROFIBRA-AZUL-M"

def check_tiny_sku():
    db = SessionLocal()
    try:
        print(f"--- SEARCHING TINY FOR SKU {SKU_TO_FIND} ---")
        tp = db.query(TinyProduct).filter(TinyProduct.sku == SKU_TO_FIND).first()
        if tp:
            print(f"\n[FOUND_ID]: {tp.id}")
            print(f"Name={tp.name}, Cost={tp.cost}")
            with open("tiny_id.txt", "w") as f:
                f.write(str(tp.id))
        else:
            print("Not found in local DB. Need to fetch from API?")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_tiny_sku()
