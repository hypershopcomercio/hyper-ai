"""
Migration Script: Numeric Keys to Categorical Keys

Migrates all MultiplierConfig entries with numeric keys to categorical keys.
Example: day_of_week "1.1" → "sabado"
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig, CalibrationHistory
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapping of numeric keys to categorical keys
# These need to be determined by inspecting current database
FACTOR_KEY_MAPPINGS = {
    'day_of_week': {
        # Will query database to find which numeric values exist
        # and map them to correct days based on calibration data
    },
    'hourly_pattern': {
        # Map numeric values to hour strings "0", "1", ..., "23"
    },
    'period_of_month': {
        # Map to "inicio", "meio", "fim"
    },
    'week_of_month': {
        # Already uses "1", "2", "3", "4" - check if any numeric
    },
    'payment_day': {
        # Already uses "5", "10", "15", etc. - check if any numeric
    },
    'mobile_hours': {
        # Should be "peak", "off_peak"
    },
    'impulse_hours': {
        # Should be "high", "normal"
    },
    'seasonal': {
        # Should be "verao", "inverno", "neutro"
    }
}

def is_numeric_key(key: str) -> bool:
    """Check if a key looks numeric (e.g., "1.1", "0.95")"""
    try:
        float(key)
        # If it's purely a number like "1", "2", "23", it's OK for hour/week/day
        # Only flag decimals
        return '.' in key
    except ValueError:
        return False

def find_numeric_keys(db):
    """Find all MultiplierConfig entries with numeric (decimal) keys"""
    logger.info("Scanning for numeric keys...")
    
    all_configs = db.query(MultiplierConfig).all()
    numeric_by_type = {}
    
    for config in all_configs:
        if is_numeric_key(config.chave):
            if config.tipo not in numeric_by_type:
                numeric_by_type[config.tipo] = []
            numeric_by_type[config.tipo].append({
                'key': config.chave,
                'value': float(config.valor),
                'calibrated': config.calibrado,
                'confidence': config.confianca
            })
    
    return numeric_by_type

def migrate_day_of_week(db):
    """
    Migrate day_of_week from numeric to categorical days.
    
    Strategy:
    1. Find all numeric day_of_week keys (e.g., "1.1", "0.932")
    2. Query CalibrationHistory to see which day each key was used
    3. Aggregate data per day
    4. Create/update categorical configs
    5. Delete numeric configs
    """
    logger.info("Migrating day_of_week...")
    
    # Find numeric keys
    numeric_configs = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'day_of_week'
    ).all()
    
    numeric_keys = [c for c in numeric_configs if is_numeric_key(c.chave)]
    
    if not numeric_keys:
        logger.info("  No numeric day_of_week keys found!")
        return
    
    logger.info(f"  Found {len(numeric_keys)} numeric keys: {[k.chave for k in numeric_keys]}")
    
    # For each numeric key, find which day it represents
    # Check CalibrationHistory to see which days used this value
    day_data = {}
    day_names = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
    
    for config in numeric_keys:
        # Check calibration history
        histories = db.query(CalibrationHistory).filter(
            CalibrationHistory.tipo_fator == 'day_of_week',
            CalibrationHistory.fator_chave == config.chave
        ).order_by(CalibrationHistory.data_calibracao.desc()).limit(10).all()
        
        if histories:
            # Try to infer day from timestamp
            for h in histories:
                day_idx = h.data_calibracao.weekday()
                day_name = day_names[day_idx]
                
                if day_name not in day_data:
                    day_data[day_name] = {
                        'values': []
                    }
                
                day_data[day_name]['values'].append(float(config.valor))
        else:
            logger.warning(f"  No history for key {config.chave}, cannot determine day")
    
    # Create/update categorical configs
    for day_name, data in day_data.items():
        avg_value = sum(data['values']) / len(data['values']) if data['values'] else 1.0
        
        existing = db.query(MultiplierConfig).filter_by(
            tipo='day_of_week',
            chave=day_name
        ).first()
        
        if existing:
            logger.info(f"  Updating {day_name}: {existing.valor} → {avg_value:.3f}")
            existing.valor = avg_value
            existing.calibrado = 'auto'
        else:
            logger.info(f"  Creating {day_name}: {avg_value:.3f}")
            new_config = MultiplierConfig(
                tipo='day_of_week',
                chave=day_name,
                valor=avg_value,
                calibrado='auto',
                confianca=50,
                locked='N'
            )
            db.add(new_config)
    
    # Delete numeric configs
    for config in numeric_keys:
        logger.info(f"  Deleting numeric key: {config.chave}")
        db.delete(config)
    
    db.commit()
    logger.info("  day_of_week migration complete!")

def migrate_hourly_pattern(db):
    """Migrate hourly_pattern to use hour strings "0"-"23" if any decimals exist"""
    logger.info("Migrating hourly_pattern...")
    
    configs = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'hourly_pattern'
    ).all()
    
    numeric_keys = [c for c in configs if is_numeric_key(c.chave)]
    
    if not numeric_keys:
        logger.info("  No numeric hourly_pattern keys found!")
        return
    
    logger.info(f"  Found {len(numeric_keys)} numeric keys - these should be hour numbers")
    # Hourly pattern should already use "0", "1", "2", etc.
    # If there are decimals, they're wrong - delete them
    for config in numeric_keys:
        logger.warning(f"  Deleting invalid hourly key: {config.chave}")
        db.delete(config)
    
    db.commit()
    logger.info("  hourly_pattern migration complete!")

def main():
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("NUMERIC KEY MIGRATION")
        logger.info("=" * 60)
        
        # Step 1: Find all numeric keys
        numeric_keys = find_numeric_keys(db)
        
        if not numeric_keys:
            logger.info("✓ No numeric keys found! Database is clean.")
            return
        
        logger.info("\nNumeric keys found:")
        for factor_type, keys in numeric_keys.items():
            logger.info(f"  {factor_type}: {len(keys)} numeric keys")
            for key_data in keys:
                logger.info(f"    - {key_data['key']}: value={key_data['value']:.3f}, samples={key_data.get('samples', 0)}")
        
        # Step 2: Migrate each factor type
        logger.info("\n" + "=" * 60)
        migrate_day_of_week(db)
        migrate_hourly_pattern(db)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Migration complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
