
import sys
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ad_tiny_link import AdTinyLink
from app.models.tiny_product import TinyProduct

ITEM_ID = "MLB5313761220"

def debug_cost():
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ITEM_ID).first()
        if not ad:
            print("Ad not found")
            return

        print(f"--- AD DETAILS ---")
        print(f"ID: {ad.id}")
        print(f"Title: {ad.title}")
        print(f"SKU: {ad.sku}")
        print(f"GTIN: {ad.gtin}")
        print(f"Cost: {ad.cost}")
        print(f"Tax: {ad.tax_cost}")
        
        print(f"\n--- TINY LINK ---")
        link = db.query(AdTinyLink).filter(AdTinyLink.ad_id == ITEM_ID).first()
        if link:
            print(f"Linked to TinyProduct ID: {link.tiny_product_id}")
            tp = db.query(TinyProduct).filter(TinyProduct.id == link.tiny_product_id).first()
            if tp:
                print(f"Tiny SKU: {tp.sku}")
                print(f"Tiny Name: {tp.name}")
                print(f"Tiny Cost: {tp.cost}")
            else:
                print("TinyProduct not found in DB")
        else:
            print("No Tiny Link found")
            
        print(f"\n--- VARIATIONS ---")
        from app.models.ad_variation import AdVariation
        vars = db.query(AdVariation).filter(AdVariation.ad_id == ITEM_ID).all()
        for v in vars:
            print(f"Var ID: {v.id}, SKU: {v.sku}, Qty: {v.available_quantity}, Cost: {v.cost}")
        
        print("\n--- CHECKING PURCHASES TABLE ---")
        try:
            res = db.execute(text("SELECT * FROM purchases LIMIT 1")).fetchall()
            print("Purchases Table Exists!")
            print(res)
        except Exception as e:
            print(f"Purchases Table Query Failed: {e}")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_cost()
