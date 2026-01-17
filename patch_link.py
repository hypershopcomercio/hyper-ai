
from app.core.database import SessionLocal
from app.models.ad_tiny_link import AdTinyLink
from app.models.tiny_product import TinyProduct


AD_ID = "MLB5313761220"
TINY_ID = "949205611"

def patch_link():
    db = SessionLocal()
    try:
        print(f"--- PATCHING LINK FOR {AD_ID} ---")
        existing = db.query(AdTinyLink).filter(AdTinyLink.ad_id == AD_ID).first()
        if existing:
            print(f"Link already exists: pointing to {existing.tiny_product_id}")
            if existing.tiny_product_id != TINY_ID:
                print(f"Updating to {TINY_ID}")
                existing.tiny_product_id = TINY_ID
                db.commit()
        else:
            print(f"Creating new link to {TINY_ID}")
            link = AdTinyLink(ad_id=AD_ID, tiny_product_id=TINY_ID)
            db.add(link)
            db.commit()
        print("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    patch_link()
