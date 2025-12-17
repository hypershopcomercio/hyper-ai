
import logging
from sqlalchemy import text
from app.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting Database Migration v4 (Free Shipping)...")
    with engine.connect() as conn:
        try:
            try:
                conn.execute(text("ALTER TABLE ads ADD COLUMN free_shipping BOOLEAN DEFAULT FALSE"))
                logger.info("Added free_shipping to ads")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info("free_shipping already exists in ads")
                else:
                    logger.warning(f"Error adding free_shipping: {e}")

            conn.commit()
            logger.info("Migration v4 completed.")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
