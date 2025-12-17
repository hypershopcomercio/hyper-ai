
from app.core.database import SessionLocal
from app.models.ad_tiny_link import AdTinyLink
from app.models.tiny_product import TinyProduct

def check_link(ad_id):
    db = SessionLocal()
    link = db.query(AdTinyLink).filter(AdTinyLink.ad_id == ad_id).first()
    if link:
        print(f"✅ Found Link for {ad_id}")
        print(f"Linked Tiny Product ID: {link.tiny_product_id}")
        
        tp = db.query(TinyProduct).filter(TinyProduct.id == link.tiny_product_id).first()
        if tp:
            print(f"✅ Linked TinyProduct FOUND in DB. Cost: {tp.cost}")
        else:
            print(f"❌ Linked TinyProduct NOT FOUND in DB (Orphan Link).")
    else:
        print(f"❌ No AdTinyLink found for {ad_id}")
    db.close()

if __name__ == "__main__":
    check_link("MLB5947812206")
