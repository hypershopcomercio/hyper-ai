
from app.core.database import SessionLocal
from app.models.ad import Ad

def find_missing_costs():
    db = SessionLocal()
    try:
        # Ads active with no cost
        missing = db.query(Ad).filter(Ad.status == 'active', Ad.cost == None).all()
        print(f"Found {len(missing)} active ads with NO COST.")
        print("-" * 60)
        for ad in missing:
            print(f"ID: {ad.id} | SKU: {ad.sku} | Title: {ad.title[:40]}...")
            # Check if it has variations?
            # We can't query relationship easily due to the comment out, check ad_variations table manual check script...
            # But bubble up logic should have handled it if valid.
            
    finally:
        db.close()

if __name__ == "__main__":
    find_missing_costs()
