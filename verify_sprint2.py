
import logging
from app.services.sync_engine import SyncEngine
from app.core.database import SessionLocal
from app.models.ml_visit import MlVisit
from app.models.ml_order import MlOrder
from app.models.tiny_stock import TinyStock
from app.models.ml_metrics_daily import MlMetricsDaily
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)

def verify_sprint2():
    print("\n--- Starting Sprint 2 Verification ---")
    
    engine = SyncEngine()
    
    # 1. Sync Visits
    print("\n[1/3] Running Sync Visits...")
    try:
        engine.sync_visits()
    except Exception as e:
        print(f"Sync Visits Failed: {e}")

    # 2. Sync Orders
    print("\n[2/3] Running Sync Orders...")
    try:
        engine.sync_orders()
    except Exception as e:
         print(f"Sync Orders Failed: {e}")

    # 3. Sync Stock
    print("\n[3/3] Running Sync Tiny Stock...")
    try:
        engine.sync_tiny_stock()
    except Exception as e:
         print(f"Sync Stock Failed: {e}")

    # 4. Check DB
    db = SessionLocal()
    print("\n--- DB Check ---")
    
    # Visits
    v_count = db.query(MlVisit).count()
    print(f"MlVisit Records: {v_count}")
    
    # Orders
    o_count = db.query(MlOrder).count()
    print(f"MlOrder Records: {o_count}")
    
    # Stock
    s_count = db.query(TinyStock).count()
    print(f"TinyStock Records: {s_count}")

    # Metrics Daily
    m_count = db.query(MlMetricsDaily).count()
    print(f"MlMetricsDaily Records: {m_count}")
    
    # Check 1 metric record details
    metric = db.query(MlMetricsDaily).order_by(MlMetricsDaily.date.desc()).first()
    if metric:
        print(f"Sample Metric ({metric.date} | Item {metric.item_id}): Visits={metric.visits}, Sales={metric.sales_qty}")
        
    db.close()

if __name__ == "__main__":
    verify_sprint2()
