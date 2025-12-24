
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_metrics_daily import MlMetricsDaily
from app.models.ad import Ad
from app.services.meli_api import MeliApiService

def check_today_visits():
    db = SessionLocal()
    api = MeliApiService(db_session=db)
    
    # Timezone BRT
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    today = now.date()
    
    print(f"Checking Visits for Date: {today}")
    
    # 1. Check DB
    count = db.query(MlMetricsDaily).filter(MlMetricsDaily.date == today).count()
    total_visits = 0
    if count > 0:
        total_visits = db.query(func.sum(MlMetricsDaily.visits)).filter(MlMetricsDaily.date == today).scalar()
    
    print(f"DB Records for Today: {count}")
    print(f"DB Total Visits Today: {total_visits}")
    
    # 2. Check API for a sample item
    ad = db.query(Ad).filter(Ad.status == 'active').first()
    if ad:
        mid = ad.id
        print(f"Checking API for Item: {mid}")
        # Fetch visits for today
        # API: /items/{id}/visits?date_from=...&date_to=...
        
        d_str = today.strftime("%Y-%m-%d")
        url = f"/items/{mid}/visits?date_from={d_str}&date_to={d_str}"
        resp = api.request("GET", url)
        if resp.status_code == 200:
            print("API Response:", resp.json())
        else:
            print(f"API Error: {resp.status_code} - {resp.text}")
            
    db.close()

from sqlalchemy import func

if __name__ == "__main__":
    check_today_visits()
