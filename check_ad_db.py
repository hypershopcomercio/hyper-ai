
from app.core.database import SessionLocal
from app.models.ad import Ad
import json

db = SessionLocal()
ad = db.query(Ad).filter(Ad.id == 'MLB3862661909').first()

if ad:
    print(f"Ad found: {ad.title}")
    print(f"Pictures field type: {type(ad.pictures)}")
    if ad.pictures:
        print(f"Pictures count: {len(ad.pictures)}")
        print("First picture sample:", ad.pictures[0] if len(ad.pictures) > 0 else "None")
    else:
        print("Pictures field is empty/None")
else:
    print("Ad not found")

db.close()
