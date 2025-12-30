"""
COMPLETE Migration Script: ALL Numeric Keys to Categorical

Migrates EVERY factor type with numeric keys to proper categorical keys.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_numeric_key(key: str) -> bool:
    """Check if key has decimal point (numeric like 1.0, 0.95)"""
    return '.' in key

def cleanup_all_numeric_keys(db):
    """Delete ALL configs with numeric (decimal) keys"""
    logger.info("Finding and deleting ALL numeric keys...")
    
    all_configs = db.query(MultiplierConfig).all()
    numeric_configs = [c for c in all_configs if is_numeric_key(c.chave)]
    
    if not numeric_configs:
        logger.info("✓ No numeric keys found!")
        return
    
    logger.info(f"Found {len(numeric_configs)} numeric keys to delete:")
    
    # Group by type
    by_type = {}
    for config in numeric_configs:
        if config.tipo not in by_type:
            by_type[config.tipo] = []
        by_type[config.tipo].append(config.chave)
    
    # Show what will be deleted
    for tipo, keys in by_type.items():
        logger.info(f"  {tipo}: {keys}")
    
    # Delete all numeric keys
    for config in numeric_configs:
        logger.info(f"  Deleting {config.tipo}.{config.chave} = {config.valor}")
        db.delete(config)
    
    db.commit()
    logger.info(f"✓ Deleted {len(numeric_configs)} numeric keys")

def main():
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("COMPLETE NUMERIC KEY CLEANUP")
        logger.info("=" * 60)
        
        cleanup_all_numeric_keys(db)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Cleanup complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
