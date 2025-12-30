"""
Delete ALL CalibrationHistory with numeric keys and regenerate forecasts
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import CalibrationHistory, MultiplierConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("NUCLEAR OPTION: Delete ALL numeric CalibrationHistory keys")
print("=" * 70)

db = SessionLocal()

try:
    # Get all CalibrationHistory
    all_hist = db.query(CalibrationHistory).all()
    
    deleted_count = 0
    
    # Check each entry
    for hist in all_hist:
        try:
            # If fator_chave can be converted to float, it's NUMERIC (BAD!)
            float(hist.fator_chave)
            logger.info(f"Deleting {hist.tipo_fator}:{hist.fator_chave} (ID {hist.id})")
            db.delete(hist)
            deleted_count += 1
        except ValueError:
            # Not numeric, keep it
            pass
    
    db.commit()
    
    print(f"\n✅ Deleted {deleted_count} CalibrationHistory entries with numeric keys")
    
    # Show what's left
    remaining = db.query(CalibrationHistory).count()
    print(f"✅ Remaining entries: {remaining}")
    
    # Stats by factor
    print("\n📊 Remaining by factor:")
    for tipo in ['day_of_week', 'seasonal', 'period_of_month', 'event', 'momentum', 'hourly_pattern']:
        count = db.query(CalibrationHistory).filter(CalibrationHistory.tipo_fator == tipo).count()
        if count > 0:
            print(f"   {tipo}: {count}")
            
            # Show sample
            sample = db.query(CalibrationHistory).filter(
                CalibrationHistory.tipo_fator == tipo
            ).limit(3).all()
            
            for s in sample:
                print(f"      - {s.fator_chave}")
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE!")
    print("Now ALL calibration will use ONLY categorical keys!")
    print("=" * 70)
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
