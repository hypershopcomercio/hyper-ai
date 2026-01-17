
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.ad import Ad
import json

def check_mapping():
    db = SessionLocal()
    try:
        print("--- SKU_MAPPING COLUMNS ---")
        try:
             res = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='sku_mapping'")).fetchall()
             print([r[0] for r in res])
             
             print("\n--- SKU_MAPPING DATA (First 3) ---")
             res = db.execute(text("SELECT * FROM sku_mapping LIMIT 3")).fetchall()
             print(res)
        except Exception as e:
             print(f"Mapping check failed: {e}")
        
        print("\n--- RAW DATA DUMP FOR MLB5313761220 ---")
        ad = db.query(Ad).filter(Ad.id == "MLB5313761220").first()
        if ad and ad.raw_data:
            print(json.dumps(ad.raw_data, indent=2, ensure_ascii=False))
        else:
            print("No raw_data found.")

    finally:
        db.close()

if __name__ == "__main__":
    check_mapping()
