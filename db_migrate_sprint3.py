
import logging
from sqlalchemy import text
from app.core.database import engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_sprint3():
    logger.info("Starting Sprint 3 Migration...")
    
    with engine.connect() as connection:
        # Add trend columns to ads table
        try:
            logger.info("Adding trend columns to ads table...")
            connection.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS visits_7d_change FLOAT"))
            connection.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS sales_7d_change FLOAT"))
            connection.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS days_of_stock FLOAT"))
            connection.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS video_id VARCHAR")) # catching up missed column
            connection.commit()
            logger.info("Trend columns added.")
        except Exception as e:
            logger.error(f"Error adding columns: {e}")
            
    logger.info("Sprint 3 Migration Completed Successfully.")

if __name__ == "__main__":
    migrate_sprint3()
