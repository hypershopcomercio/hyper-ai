import sys
import os
from sqlalchemy import func

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ad import Ad

def inspect_stock_risk():
    db = SessionLocal()
    try:
        # Rule: status='active', days_of_stock < 30, days_of_stock > 0
        risks = db.query(Ad).filter(Ad.status == 'active', Ad.days_of_stock < 30, Ad.days_of_stock > 0).all()
        
        total_value = sum((ad.price or 0) * (ad.available_quantity or 0) for ad in risks)
        
        print(f"Total Cards Found: {len(risks)}")
        print(f"Total Value (R$): {total_value:,.2f}")
        
        print("\n--- Top 5 Risks ---")
        top_5 = sorted(risks, key=lambda x: x.days_of_stock)[:5]
        for ad in top_5:
            val = (ad.price or 0) * (ad.available_quantity or 0)
            print(f"ID: {ad.id} | Title: {ad.title[:30]}... | Stock: {ad.available_quantity} | Price: {ad.price} | Value: {val} | Days: {ad.days_of_stock}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_stock_risk()
