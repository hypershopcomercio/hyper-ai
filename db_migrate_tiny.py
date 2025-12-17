
import logging
from sqlalchemy import text
from app.core.database import Base, engine, SessionLocal
from app.models.tiny_product import TinyProduct
from app.models.ad_tiny_link import AdTinyLink
from app.models.ad import Ad

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    logger.info("Creating new tables (tiny_products, ad_tiny_links)...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Checking for new columns in 'ads' table...")
    db = SessionLocal()
    try:
        # Check if column margin_percent exists
        # SQLite pragma table_info
        result = db.execute(text("PRAGMA table_info(ads)")).fetchall()
        columns = [row[1] for row in result]
        
        new_columns = {
            "margin_percent": "FLOAT",
            "margin_value": "FLOAT",
            "is_margin_alert": "BOOLEAN DEFAULT 0",
            "commission_cost": "FLOAT DEFAULT 0",
            "shipping_cost": "FLOAT DEFAULT 0",
            "tax_cost": "FLOAT DEFAULT 0"
        }
        
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                logger.info(f"Adding column {col_name} to ads table...")
                db.execute(text(f"ALTER TABLE ads ADD COLUMN {col_name} {col_type}"))
        
        db.commit()
        logger.info("Migration completed.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run()
