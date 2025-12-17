
import logging
from sqlalchemy import text
from app.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting Database Migration v3 (Auth & Fields)...")
    with engine.connect() as conn:
        try:
            # 1. OAuth Tokens: Add seller_id
            try:
                conn.execute(text("ALTER TABLE oauth_tokens ADD COLUMN seller_id VARCHAR"))
                logger.info("Added seller_id to oauth_tokens")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info("seller_id already exists in oauth_tokens")
                else:
                    logger.warning(f"Error adding seller_id: {e}")

            # 2. Ads: Add new fields
            new_fields = [
                ("original_price", "FLOAT"),
                ("is_full", "BOOLEAN DEFAULT FALSE"),
                ("is_catalog", "BOOLEAN DEFAULT FALSE"),
                ("health_score", "FLOAT DEFAULT 0.0")
            ]
            
            for field, type_ in new_fields:
                try:
                    conn.execute(text(f"ALTER TABLE ads ADD COLUMN {field} {type_}"))
                    logger.info(f"Added {field} to ads")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        logger.info(f"{field} already exists in ads")
                    else:
                        logger.warning(f"Error adding {field}: {e}")

            # 3. Metrics: Add gross_revenue
            try:
                conn.execute(text("ALTER TABLE metrics ADD COLUMN gross_revenue FLOAT DEFAULT 0.0"))
                logger.info("Added gross_revenue to metrics")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info("gross_revenue already exists in metrics")
                else:
                    logger.warning(f"Error adding gross_revenue: {e}")

            conn.commit()
            logger.info("Migration v3 completed.")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
