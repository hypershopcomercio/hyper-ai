import sys
import os
sys.path.append(os.getcwd())
from app.api.endpoints.dashboard import SessionLocal
from app.models.ad import Ad

def check_costs():
    db = SessionLocal()
    try:
        total_ads = db.query(Ad).count()
        ads_with_cost = db.query(Ad).filter(Ad.cost > 0).count()
        ads_with_tiny_id = db.query(Ad).filter(Ad.tiny_id != None).count()
        
        print(f"Total Ads: {total_ads}")
        print(f"Ads with Cost: {ads_with_cost}")
        print(f"Ads with Tiny ID: {ads_with_tiny_id}")
        
        if ads_with_cost > 0:
            sample = db.query(Ad).filter(Ad.cost > 0).first()
            print(f"Sample: {sample.title} - Cost: {sample.cost}")
    finally:
        db.close()

if __name__ == "__main__":
    check_costs()
