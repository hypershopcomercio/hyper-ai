
import logging
from app.services.sync_engine import SyncEngine
from app.core.database import SessionLocal
from app.models.sale import Sale

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sales_sync():
    logger.info("Testing Sales Sync...")
    engine = SyncEngine()
    engine.sync_sales()
    
    # Check results
    db = SessionLocal()
    sales_count = db.query(Sale).count()
    logger.info(f"Total Sales in DB: {sales_count}")
    
    if sales_count > 0:
        last_sale = db.query(Sale).order_by(Sale.date_created.desc()).first()
        logger.info(f"Latest Sale ID: {last_sale.id}")
        logger.info(f"  Total Amount: {last_sale.total_amount}")
        logger.info(f"  Commission: {last_sale.commission_cost}")
        logger.info(f"  Net Margin: {last_sale.net_margin}")
    
    db.close()

if __name__ == "__main__":
    test_sales_sync()
