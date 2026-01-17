
from app.core.database import SessionLocal
from app.models.ad import Ad
db = SessionLocal()

total = db.query(Ad).filter(Ad.status == 'active').count()
zero_tax = db.query(Ad).filter(Ad.status == 'active', Ad.tax_cost == 0).count()

print(f"Active Ads: {total}")
print(f"Ads with Zero Tax: {zero_tax}")

if zero_tax > 0:
    sample = db.query(Ad).filter(Ad.status == 'active', Ad.tax_cost == 0).first()
    print(f"Sample Zero Tax Ad: {sample.id}, Price: {sample.price}")

db.close()
