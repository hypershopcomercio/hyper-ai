
from app.core.database import SessionLocal
from app.models.ad import Ad

def verify_sprint3():
    db = SessionLocal()
    print("\n--- Sprint 3 Verification ---")
    
    # 1. Check Trends
    print("\n[Trends Check]")
    # Get ads with non-null trend AND non-zero (to prove something happened)
    # Or just non-null
    trends = db.query(Ad).filter(Ad.visits_7d_change.isnot(None)).limit(5).all()
    if not trends:
        print("WARNING: No ads have visits_7d_change calculated.")
    
    for ad in trends:
        print(f"Ad {ad.id} | Visits 7d: {ad.visits_7d_change}% | Sales 7d: {ad.sales_7d_change}% | DOS: {ad.days_of_stock}")

    # 2. Check Margins
    print("\n[Margin Check]")
    margins = db.query(Ad).filter(Ad.margin_percent.isnot(None)).limit(5).all()
    if not margins:
        print("WARNING: No ads have margin updated.")
        
    for ad in margins:
        print(f"Ad {ad.id} | Price: {ad.price} | Tax Cost: {ad.tax_cost} | Com: {ad.commission_cost} | Margin: {ad.margin_percent:.2f}%")

    # 3. Count
    total_processed = db.query(Ad).filter(Ad.visits_7d_change.isnot(None)).count()
    print(f"\nTotal Ads with Processed Trends: {total_processed}")

    db.close()

if __name__ == "__main__":
    verify_sprint3()
