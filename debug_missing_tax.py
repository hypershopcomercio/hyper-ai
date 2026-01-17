
from app.core.database import SessionLocal
from app.models.ad import Ad
from sqlalchemy import func

db = SessionLocal()

# Group by Status for ads with tax_cost = 0
stats = db.query(Ad.status, func.count(Ad.id)).filter(
    (Ad.tax_cost == 0) | (Ad.tax_cost == None)
).group_by(Ad.status).all()

print("Ads with Tax Cost = 0 (Grouped by Status):")
for status, count in stats:
    print(f"[{status}]: {count}")

# Check if any active ad has 0 tax
active_zeros = db.query(Ad).filter(Ad.status == 'active', (Ad.tax_cost == 0) | (Ad.tax_cost == None)).all()
if active_zeros:
    print(f"\nExample Active Ads with Zero Tax ({len(active_zeros)}):")
    for ad in active_zeros[:5]:
        print(f"- {ad.id}: Price={ad.price}, Title={ad.title[:30]}...")
else:
    print("\nNo ACTIVE ads have zero tax. (All active ads are calculated).")

db.close()
