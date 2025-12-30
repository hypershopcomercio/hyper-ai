"""
Delete invalid listing_type and hourly_pattern subfactors
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig, CalibrationHistory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("CLEANING INVALID SUBFACTORS")
print("=" * 70)

db = SessionLocal()

try:
    # 1. Delete invalid listing_type entries
    print("\n1. Deleting invalid listing_type entries...")
    
    # Only classico and premium are valid
    valid_listing_types = ['classico', 'premium']
    
    invalid_listing = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'listing_type',
        ~MultiplierConfig.chave.in_(valid_listing_types)
    ).all()
    
    for config in invalid_listing:
        logger.info(f"   Deleting invalid listing_type: {config.chave}")
        db.delete(config)
    
    print(f"   ✅ Deleted {len(invalid_listing)} invalid listing_type entries")
    
    # Delete from CalibrationHistory too
    invalid_listing_hist = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'listing_type',
        ~CalibrationHistory.fator_chave.in_(valid_listing_types)
    ).all()
    
    for hist in invalid_listing_hist:
        db.delete(hist)
    
    print(f"   ✅ Deleted {len(invalid_listing_hist)} invalid CalibrationHistory entries")
    
    # 2. Format hourly_pattern keys to "00h" format
    print("\n2. Formatting hourly_pattern keys to 00h-23h...")
    
    hourly_configs = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'hourly_pattern'
    ).all()
    
    formatted_count = 0
    for config in hourly_configs:
        try:
            hour_num = int(config.chave)
            new_key = f"{hour_num:02d}h"
            
            if config.chave != new_key:
                # Check if formatted version already exists
                existing = db.query(MultiplierConfig).filter(
                    MultiplierConfig.tipo == 'hourly_pattern',
                    MultiplierConfig.chave == new_key
                ).first()
                
                if existing:
                    logger.info(f"   Deleting duplicate: {config.chave}")
                    db.delete(config)
                else:
                    logger.info(f"   Formatting {config.chave} → {new_key}")
                    config.chave = new_key
                    formatted_count += 1
        except ValueError:
            logger.warning(f"   Skipping invalid hourly_pattern key: {config.chave}")
    
    print(f"   ✅ Formatted {formatted_count} hourly_pattern keys")
    
    # Format CalibrationHistory too
    hourly_hist = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'hourly_pattern'
    ).all()
    
    hist_formatted = 0
    for hist in hourly_hist:
        try:
            hour_num = int(hist.fator_chave)
            new_key = f"{hour_num:02d}h"
            
            if hist.fator_chave != new_key:
                hist.fator_chave = new_key
                hist_formatted += 1
        except ValueError:
            pass
    
    print(f"   ✅ Formatted {hist_formatted} CalibrationHistory hourly_pattern keys")
    
    db.commit()
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 70)
    print("\nRemaining subfactors:")
    print(f"   listing_type: {db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'listing_type').count()}")
    print(f"   hourly_pattern: {db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'hourly_pattern').count()}")
    
except Exception as e:
    logger.error(f"Cleanup failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
