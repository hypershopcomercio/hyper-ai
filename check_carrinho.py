
from app.core.database import SessionLocal
from app.models.ad_variation import AdVariation
from app.models.ad import Ad

def check_carrinho():
    db = SessionLocal()
    ad_id = "MLB5654002954"
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        print(f"Ad: {ad.title} (SKU: {ad.sku})")
        
        vars = db.query(AdVariation).filter(AdVariation.ad_id == ad_id).all()
        print(f"Variations Found: {len(vars)}")
        for v in vars:
            print(f" - Var ID: {v.id} | SKU: {v.sku} | Cost: {v.cost}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_carrinho()
