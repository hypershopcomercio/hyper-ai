
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ad_variation import AdVariation

def check_assento():
    db = SessionLocal()
    # "Assento De Vaso" - MLB4319544335
    ad_id = "MLB4319544335"
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if ad:
        print(f"Title: {ad.title}")
        print(f"Cost: {ad.cost}")
        print(f"SKU: {ad.sku}")
        
        vars = db.query(AdVariation).filter(AdVariation.ad_id == ad_id).all()
        print(f"Variations: {len(vars)}")
        for v in vars:
            print(f" - Var SKU: {v.sku}, Cost: {v.cost}")
    else:
        print("Ad not found")
    db.close()

if __name__ == "__main__":
    check_assento()
