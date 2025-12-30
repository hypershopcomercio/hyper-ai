"""
Rename CalibrationHistory entries from deleted keys to new keys
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
print("RENAME CALIBRATIONHISTORY KEYS")
print("=" * 70)

db = SessionLocal()

try:
    # Rename momentum:default → momentum:normal
    print("\n1️⃣ Momentum: Renaming 'default' → 'normal'...")
    
    momentum_default_hist = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'momentum',
        CalibrationHistory.fator_chave == 'default'
    ).all()
    
    for h in momentum_default_hist:
        h.fator_chave = 'normal'
    
    print(f"   ✅ Renamed {len(momentum_default_hist)} entries")
    
    # Rename event:none → event:normal
    print("\n2️⃣ Event: Renaming 'none' → 'normal'...")
    
    event_none_hist = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'event',
        CalibrationHistory.fator_chave == 'none'
    ).all()
    
    for h in event_none_hist:
        h.fator_chave = 'normal'
    
    print(f"   ✅ Renamed {len(event_none_hist)} entries")
    
    db.commit()
    
    # Show updated stats
    print("\n" + "=" * 70)
    print("UPDATED CALIBRATIONHISTORY:")
    print("=" * 70)
    
    print("\n📊 Momentum:")
    momentum_hist = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'momentum'
    ).all()
    
    # Group by key
    by_key = {}
    for h in momentum_hist:
        by_key.setdefault(h.fator_chave, []).append(h)
    
    for key, entries in by_key.items():
        print(f"   {key}: {len(entries)} calibrations")
    
    print("\n📊 Event:")
    event_hist = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'event'
    ).all()
    
    by_key = {}
    for h in event_hist:
        by_key.setdefault(h.fator_chave, []).append(h)
    
    for key, entries in list(by_key.items())[:5]:
        print(f"   {key}: {len(entries)} calibrations")
    
    print(f"\n✅ Total momentum calibrations: {len(momentum_hist)}")
    print(f"✅ Total event calibrations: {len(event_hist)}")
    
    print("\n" + "=" * 70)
    print("✅ RENAMING COMPLETE!")
    print("=" * 70)
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
