
from app.core.database import SessionLocal
from app.models.ml_metrics_daily import MlMetricsDaily
from datetime import date
from sqlalchemy import func

def check_db():
    db = SessionLocal()
    today = date(2026, 1, 3) # Hardcoded to user's "today"
    
    count = db.query(MlMetricsDaily).filter(MlMetricsDaily.date == today).count()
    total_visits = db.query(func.sum(MlMetricsDaily.visits)).filter(MlMetricsDaily.date == today).scalar() or 0
    
    print(f"Date: {today}")
    print(f"Records: {count}")
    print(f"Total Visits: {total_visits}")
    
    ids = db.query(MlMetricsDaily.item_id, MlMetricsDaily.visits).filter(MlMetricsDaily.date == today).limit(5).all()
    print("Sample:", ids)

if __name__ == "__main__":
    check_db()
