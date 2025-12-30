import sys
import os
import logging
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_invalid_keys():
    db = SessionLocal()
    try:
        logger.info("Starting cleanup of invalid multiplier keys...")
        
        # specific targets to remove
        targets = [
            {'tipo': 'event', 'chave': 'none'},
            {'tipo': 'impulse_hours', 'chave': 'high'},
            {'tipo': 'momentum', 'chave': 'default'}
        ]
        
        deleted_count = 0
        
        for target in targets:
            config = db.query(MultiplierConfig).filter(
                MultiplierConfig.tipo == target['tipo'],
                MultiplierConfig.chave == target['chave']
            ).first()
            
            if config:
                logger.info(f"Removing invalid config: [{config.tipo}] {config.chave} = {config.valor}")
                db.delete(config)
                deleted_count += 1
            else:
                logger.info(f"Target not found (already clean): [{target['tipo']}] {target['chave']}")
        
        if deleted_count > 0:
            db.commit()
            logger.info(f"Successfully removed {deleted_count} invalid keys.")
        else:
            logger.info("No invalid keys found.")
            
    except Exception as e:
        logger.error(f"Error repairing keys: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_invalid_keys()
