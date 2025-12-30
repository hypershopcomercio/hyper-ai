"""
Fix CalibrationHistory to use categorical keys for ALL factors
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import CalibrationHistory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("FIXING CALIBRATIONHISTORY CATEGORICAL KEYS")
print("=" * 70)

db = SessionLocal()

try:
    # Migration mappings for ALL factors
    migrations = {
        'day_of_week': {
            '0': 'segunda', '1': 'terca', '2': 'quarta', '3': 'quinta',
            '4': 'sexta', '5': 'sabado', '6': 'domingo',
            '0.0': 'segunda', '1.0': 'terca', '2.0': 'quarta', '3.0': 'quinta',
            '4.0': 'sexta', '5.0': 'sabado', '6.0': 'domingo',
            '1.1': 'segunda', '1.25': 'segunda'
        },
        'seasonal': {
            '0': 'verao', '0.0': 'verao',
            '1': 'inverno', '1.0': 'inverno',
            '2': 'neutro', '2.0': 'neutro'
        },
        'period_of_month': {
            '0': 'inicio', '0.0': 'inicio',
            '1': 'meio', '1.0': 'meio',
            '2': 'fim', '2.0': 'fim'
        },
        'mobile_hours': {
            '0': 'off_peak', '1': 'peak',
            '0.0': 'off_peak', '1.0': 'peak'
        },
        'impulse_hours': {
            '0': 'normal', '1': 'high',
            '0.0': 'normal', '1.0': 'high'
        },
        'event': {
            '0': 'none', '0.0': 'none',
            '1': '12-25', '1.0': '12-25',  # Christmas example
            '2': '01-01', '2.0': '01-01'   # New Year example
        },
        'medal': {
            '0': 'silver', '0.0': 'silver',
            '1': 'gold', '1.0': 'gold',
            '2': 'platinum', '2.0': 'platinum'
        }
    }
    
    print("\n📋 Migrating CalibrationHistory keys...")
    
    all_history = db.query(CalibrationHistory).all()
    migrated_count = 0
    deleted_count = 0
    
    for hist in all_history:
        if hist.tipo_fator in migrations:
            old_key = hist.fator_chave
            mapping = migrations[hist.tipo_fator]
            
            if old_key in mapping:
                new_key = mapping[old_key]
                
                # Check if new key already exists
                existing = db.query(CalibrationHistory).filter(
                    CalibrationHistory.tipo_fator == hist.tipo_fator,
                    CalibrationHistory.fator_chave == new_key,
                    CalibrationHistory.data_calibracao == hist.data_calibracao
                ).first()
                
                if existing:
                    # Delete duplicate
                    logger.info(f"   Deleting duplicate: {hist.tipo_fator}:{old_key}")
                    db.delete(hist)
                    deleted_count += 1
                else:
                    # Migrate
                    logger.info(f"   Migrating {hist.tipo_fator}:{old_key} → {new_key}")
                    hist.fator_chave = new_key
                    migrated_count += 1
    
    db.commit()
    
    print(f"\n✅ Migrated {migrated_count} CalibrationHistory entries")
    print(f"✅ Deleted {deleted_count} duplicate entries")
    
    # Statistics
    print("\n" + "=" * 70)
    print("CALIBRATION HISTORY BY FACTOR:")
    print("=" * 70)
    
    for tipo_name in ['day_of_week', 'seasonal', 'period_of_month', 'mobile_hours', 'impulse_hours', 'event', 'medal', 'hourly_pattern']:
        count = db.query(CalibrationHistory).filter(CalibrationHistory.tipo_fator == tipo_name).count()
        print(f"   {tipo_name}: {count} entries")
    
    print("\n✅ All CalibrationHistory now uses CATEGORICAL KEYS!")
    
except Exception as e:
    logger.error(f"Migration failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
