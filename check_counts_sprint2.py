
from app.core.database import SessionLocal
from app.models.ml_visit import MlVisit
from app.models.ml_order import MlOrder
from app.models.tiny_stock import TinyStock
from app.models.ml_metrics_daily import MlMetricsDaily
from sqlalchemy import text

def check():
    db = SessionLocal()
    print("--- DB Counts Sprint 2 ---")
    print(f"MlVisit: {db.query(MlVisit).count()}")
    print(f"MlOrder: {db.query(MlOrder).count()}")
    print(f"TinyStock: {db.query(TinyStock).count()}")
    print(f"MlMetricsDaily: {db.query(MlMetricsDaily).count()}")
    
    # Check Logs
    log = db.execute(text("SELECT * FROM sync_logs ORDER BY id DESC LIMIT 1")).fetchone()
    if log:
         print(f"Last Log: {log.type} / {log.status} / Processed: {log.records_processed} / Success: {log.records_success}")
    
    db.close()

if __name__ == "__main__":
    check()
