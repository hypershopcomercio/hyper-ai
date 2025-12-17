
import logging
from sqlalchemy import text
from app.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Migrating Metrics table...")
    with engine.connect() as conn:
        try:
            try:
                conn.execute(text("ALTER TABLE metrics ADD COLUMN gross_revenue FLOAT DEFAULT 0.0"))
                logger.info("Added gross_revenue to metrics")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info("gross_revenue already exists in metrics")
                else:
                    logger.warning(f"Error adding gross_revenue: {e}")
            conn.commit()
            logger.info("Metrics Migration completed.")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
