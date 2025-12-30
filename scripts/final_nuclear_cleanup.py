"""
Delete ALL numeric and duplicate factor keys from MultiplierConfig and CalibrationHistory
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
print("NUCLEAR CLEANUP: DELETE ALL NUMERIC KEYS")
print("=" * 70)

db = SessionLocal()

try:
    # Get ALL configs
    all_configs = db.query(MultiplierConfig).all()
    
    deleted = 0
    
    # DELETE ANY with numeric keys
    print("\n🧹 Deleting numeric keys from MultiplierConfig...")
    for config in all_configs:
        try:
            # Try to convert to float - if succeeds, it's numeric (BAD!)
            float(config.chave)
            logger.info(f"   Deleting {config.tipo}:{config.chave} (ID {config.id})")
            db.delete(config)
            deleted += 1
        except ValueError:
            # Not numeric, keep it
            pass
    
    db.commit()
    print(f"✅ Deleted {deleted} MultiplierConfig entries with numeric keys")
    
    # NOW DELETE FROM CALIBRATIONHISTORY
    all_cal = db.query(CalibrationHistory).all()
    deleted_cal = 0
    
    print("\n🧹 Deleting numeric keys from CalibrationHistory...")
    for cal in all_cal:
        try:
            float(cal.fator_chave)
            logger.info(f"   Deleting {cal.tipo_fator}:{cal.fator_chave}")
            db.delete(cal)
            deleted_cal += 1
        except ValueError:
            pass
    
    db.commit()
    print(f"✅ Deleted {deleted_cal} CalibrationHistory entries with numeric keys")
    
    # DELETE DUPLICATE event:none entries
    print("\n🧹 Consolidating duplicate event:none...")
    event_nones = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'event',
        MultiplierConfig.chave == 'none'
    ).all()
    
    if len(event_nones) > 1:
        # Keep the best (auto-calibrated > manual, higher confidence)
        best = max(event_nones, key=lambda x: (
            1 if x.calibrado == 'auto' else 0,
            x.confianca or 0,
            x.atualizado_em or x.id
        ))
        
        print(f"   Found {len(event_nones)} event:none entries")
        print(f"   ✅ Keeping ID {best.id}: {best.valor} ({best.calibrado})")
        
        for e in event_nones:
            if e.id != best.id:
                print(f"   ❌ Deleting ID {e.id}: {e.valor}")
                db.delete(e)
        
        db.commit()
        print(f"✅ Consolidated event:none")
    else:
        print("   ✅ No event:none duplicates found")
    
    # FINAL CHECK
    print("\n" + "=" * 70)
    print("FINAL CHECK:")
    print("=" * 70)
    
    remaining = db.query(MultiplierConfig).all()
    numeric_found = []
    
    for c in remaining:
        try:
            float(c.chave)
            numeric_found.append(f"{c.tipo}:{c.chave}")
        except ValueError:
            pass
    
    if numeric_found:
        print(f"\n⚠️  WARNING: Still found {len(numeric_found)} numeric keys:")
        for n in numeric_found:
            print(f"   {n}")
    else:
        print("\n✅ NO NUMERIC KEYS FOUND - DATABASE IS CLEAN!")
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 70)
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
