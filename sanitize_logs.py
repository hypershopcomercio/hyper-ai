import sys
import os
import json
import logging

# Add app directory to path
PROJECT_ROOT = r'c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data'
sys.path.append(PROJECT_ROOT)

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_logs():
    db = SessionLocal()
    try:
        logs = db.query(ForecastLog).all()
        logger.info(f"Found {len(logs)} logs to sanitize.")
        
        total_removed = 0
        logs_modified = 0
        
        for log in logs:
            if not log.fatores_usados:
                continue
                
            # Handle JSON string or dict
            factors = log.fatores_usados
            is_str = False
            if isinstance(factors, str):
                try:
                    factors = json.loads(factors)
                    is_str = True
                except:
                    continue
            
            if '_product_mix' not in factors:
                continue
                
            product_mix = factors['_product_mix']
            original_count = len(product_mix)
            
            # --- FILTER LOGIC ---
            # 1. Remove if stock <= 0 (General Rule)
            # 2. Remove specifically 'Bar Cooler' (MLB3964133363) as requested manually
            # 3. Remove specifically 'Kit Refrigerador Cooler' as requested manually
            
            new_mix = []
            for prod in product_mix:
                stock = prod.get('stock') or 0
                title = prod.get('title', '')
                mlb_id = prod.get('mlb_id', '')
                
                # Manual Exclusions
                if 'MLB3964133363' in mlb_id or 'Bar Cooler' in title or 'Kit Refrigerador Cooler' in title:
                    logger.info(f"Removing Manual Item: {title} (Stock: {stock}) from Log {log.id}")
                    continue
                    
                # General Rule
                if stock <= 0:
                    # logger.info(f"Removing Zero Stock: {title} from Log {log.id}")
                    continue
                    
                new_mix.append(prod)
            
            # Update if changed
            if len(new_mix) < original_count:
                factors['_product_mix'] = new_mix
                
                if is_str:
                    log.fatores_usados = json.dumps(factors)
                else:
                    log.fatores_usados = factors
                    
                logs_modified += 1
                total_removed += (original_count - len(new_mix))
                
                # Force update flag to unsure sqlalchemy picks it up
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(log, "fatores_usados")
                
        db.commit()
        logger.info(f"Sanitization Complete.")
        logger.info(f"Logs Modified: {logs_modified}")
        logger.info(f"Total Products Removed: {total_removed}")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error sanitizing logs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sanitize_logs()
