from app.core.database import SessionLocal
from app.models.ad import Ad

db = SessionLocal()
try:
    print("--- CHECKING ADS DATA ---")
    
    # Check Visits
    with_visits = db.query(Ad).filter(Ad.total_visits > 0).count()
    total = db.query(Ad).count()
    print(f"Total Ads: {total}")
    print(f"Ads with Visits > 0: {with_visits}")
    
    # Check Shipping Mode
    with_shipping = db.query(Ad).filter(Ad.shipping_mode.isnot(None)).count()
    print(f"Ads with Shipping Mode: {with_shipping}")
    
    # Sample
    sample = db.query(Ad).filter(Ad.total_visits > 0).first()
    if sample:
        print(f"\nSample: {sample.id}")
        print(f"  Title: {sample.title}")
        print(f"  Visits: {sample.total_visits}")
        print(f"  Shipping: {sample.shipping_mode}")
        print(f"  Listing Type: {sample.listing_type_id}")
    else:
        print("No ads with visits found.")
        # Check one without visits
        sample = db.query(Ad).first()
        if sample:
             print(f"\nSample (Zero Visits): {sample.id}")
             print(f"  Title: {sample.title}")
             print(f"  Visits: {sample.total_visits}")

finally:
    db.close()
