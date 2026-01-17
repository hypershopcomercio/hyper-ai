
from app.core.database import SessionLocal
from app.models.ad import Ad

db = SessionLocal()
ad_id = 'MLB85238117228' # From screenshot/ocr
# The ID in screenshot looks like MLB85238117228 but maybe I should check approximate.
# The user says "este aqui". I should use the one from the screenshot.
# Let's try to wildcard search if exact match fails, or just list ads with 'Piscina Intex' in title.

ad = db.query(Ad).filter(Ad.id == ad_id).first()
if not ad:
    # Try searching by title
    print(f"ID {ad_id} not found. Searching by title...")
    ad = db.query(Ad).filter(Ad.title.ilike('%Piscina Intex Por Do Sol%')).first()

if ad:
    print(f"AD FOUND: {ad.id}")
    print(f"Status: {ad.status}")
    print(f"Price: {ad.price}")
    print(f"Tax Cost: {ad.tax_cost}")
    print(f"Margin: {ad.margin_value} ({ad.margin_percent}%)")
    print(f"Available Qty: {ad.available_quantity}")
else:
    print("Ad NOT FOUND.")

db.close()
