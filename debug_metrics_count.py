
import logging
import sys
from app.core.database import SessionLocal
from app.models.ml_metrics_daily import MlMetricsDaily
from sqlalchemy import desc

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def check_metrics():
    db = SessionLocal()
    try:
        # Get an ad with high visit count or just any ad
        # Let's pick one that has data
        ad_id_row = db.query(MlMetricsDaily.item_id).first()
        if not ad_id_row:
            print("No metrics found in DB.")
            return

        item_id = ad_id_row[0]
        
        # Check Total Count for this item
        count = db.query(MlMetricsDaily).filter(MlMetricsDaily.item_id == item_id).count()
        print(f"Item {item_id} has {count} daily metric records.")
        
        # Check Date Range
        min_date = db.query(MlMetricsDaily.date).filter(MlMetricsDaily.item_id == item_id).order_by(MlMetricsDaily.date.asc()).first()
        max_date = db.query(MlMetricsDaily.date).filter(MlMetricsDaily.item_id == item_id).order_by(MlMetricsDaily.date.desc()).first()
        
        print(f"Range: {min_date[0]} to {max_date[0]}")
        
        # Simulate API query
        api_results = db.query(MlMetricsDaily).filter(MlMetricsDaily.item_id == item_id).order_by(MlMetricsDaily.date.asc()).limit(90).all()
        print(f"API Query (ASC limit 90) returned {len(api_results)} records.")
        if api_results:
             print(f"API First: {api_results[0].date}, API Last: {api_results[-1].date}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_metrics()
