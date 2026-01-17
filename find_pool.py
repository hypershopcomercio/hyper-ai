
from app.core.database import SessionLocal
from app.models.ad import Ad

db = SessionLocal()
print("\n--- POOL ADS ---")
ads = db.query(Ad).filter(Ad.title.ilike('%Piscina%')).limit(10).all()
for ad in ads:
    print(f"ID: {ad.id} | Title: {ad.title[:50]}... | Pics: {len(ad.pictures) if ad.pictures else 0}")
db.close()
