
import logging
from app.core.database import Base, engine

# Import all models to ensure they are registered in Base.metadata
# We need to scan app/models to know what to import, 
# but I will import the ones I know of based on previous interactions.
from app.models.ad import Ad
from app.models.metric import Metric
from app.models.oauth_token import OAuthToken
from app.models.tiny_product import TinyProduct
from app.models.ad_tiny_link import AdTinyLink
from app.models.system_log import SystemLog
from app.models.alert import Alert
from app.models.system_config import SystemConfig
from app.models.forecast_learning import ForecastLog, CalibrationHistory, MultiplierConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    logger.info("Creating tables in PostgreSQL...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
