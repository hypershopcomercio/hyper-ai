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

def fix_momentum_keys():
    db = SessionLocal()
    try:
        logger.info("Checking for corrupted momentum keys...")
        
        # Find bad configs
        # Bad keys are those with spaces or overly long (descriptions)
        bad_configs = db.query(MultiplierConfig).filter(
            MultiplierConfig.tipo == 'momentum'
        ).all()
        
        deleted_count = 0
        valid_keys = ['up', 'down', 'neutral', 'strong_up', 'strong_down']
        
        for config in bad_configs:
            # Check if key is invalid
            # 1. Contains spaces (descriptions often do)
            # 2. Starts with "Vendas" or similar description text
            # 3. Not in our known valid set (optional, maybe too strict)
            
            is_bad = False
            if ' ' in config.chave:
                is_bad = True
            elif len(config.chave) > 30: # arbitrary safety limit
                is_bad = True
            elif config.chave.startswith('Vendas'):
                is_bad = True
                
            if is_bad:
                logger.info(f"Removing invalid config: [{config.tipo}] {config.chave} = {config.valor}")
                db.delete(config)
                deleted_count += 1
            else:
                logger.info(f"Keeping valid config: [{config.tipo}] {config.chave} = {config.valor}")
        
        if deleted_count > 0:
            db.commit()
            logger.info(f"Successfully removed {deleted_count} invalid momentum keys.")
        else:
            logger.info("No invalid momentum keys found.")
            
        # Optional: Ensure default valid keys exist
        # This isn't strictly necessary as they are dynamic, but good for UI
            
    except Exception as e:
        logger.error(f"Error repairing keys: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_momentum_keys()
