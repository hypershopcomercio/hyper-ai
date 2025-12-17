
from app.core.database import SessionLocal
from app.models.ad import Ad

def check():
    db = SessionLocal()
    # "Fechadura Vitrine"
    ad = db.query(Ad).filter(Ad.id == "MLB5947812206").first()
    if ad:
        print(f"Title: {ad.title}")
        print(f"Cost: {ad.cost}")
    else:
        print("Ad not found")
    db.close()

if __name__ == "__main__":
    check()
