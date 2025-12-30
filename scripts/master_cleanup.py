"""
MASTER cleanup: Remove ALL numeric keys and consolidate duplicates
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("MASTER CLEANUP: ALL FACTORS")
print("=" * 70)

db = SessionLocal()

try:
    # Get ALL configs
    all_configs = db.query(MultiplierConfig).all()
    
    deleted_numeric = 0
    
    # Step 1: DELETE ALL with numeric keys
    print("\n🧹 Step 1: Deleting entries with numeric keys...")
    
    for config in all_configs:
        try:
            # If chave can be converted to float, it's NUMERIC (BAD!)
            float(config.chave)
            logger.info(f"   Deleting {config.tipo}:{config.chave} (ID {config.id})")
            db.delete(config)
            deleted_numeric += 1
        except ValueError:
            # Not numeric, keep it
            pass
    
    db.commit()
    print(f"✅ Deleted {deleted_numeric} entries with numeric keys")
    
    # Step 2: CONSOLIDATE duplicates
    print("\n🔄 Step 2: Consolidating duplicates...")
    
    # Reload after deletions
    all_configs = db.query(MultiplierConfig).all()
    
    # Group by tipo + chave
    grouped = {}
    for config in all_configs:
        key = f"{config.tipo}.{config.chave}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(config)
    
    deleted_dupes = 0
    
    for key, entries in grouped.items():
        if len(entries) > 1:
            print(f"\n🔍 Found {len(entries)} entries for '{key}':")
            
            # Keep the best one (auto-calibrated > manual, higher confidence, most recent)
            best = max(entries, key=lambda x: (
                1 if x.calibrado == 'auto' else 0,
                x.confianca or 0,
                x.atualizado_em or x.id
            ))
            
            print(f"   ✅ Keeping ID {best.id}: {best.valor}")
            
            # Delete others
            for e in entries:
                if e.id != best.id:
                    print(f"   ❌ Deleting ID {e.id}: {e.valor}")
                    db.delete(e)
                    deleted_dupes += 1
    
    db.commit()
    print(f"\n✅ Deleted {deleted_dupes} duplicate entries")
    
    # Step 3: SHOW FINAL STATS
    print("\n" + "=" * 70)
    print("FINAL STATISTICS:")
    print("=" * 70)
    
    all_final = db.query(MultiplierConfig).all()
    
    # Group by tipo
    by_tipo = {}
    for config in all_final:
        if config.tipo not in by_tipo:
            by_tipo[config.tipo] = []
        by_tipo[config.tipo].append(config)
    
    for tipo, configs in sorted(by_tipo.items()):
        print(f"\n📊 {tipo}: {len(configs)} entries")
        for c in configs[:5]:  # Show first 5
            print(f"   {c.chave}: {c.valor}")
        if len(configs) > 5:
            print(f"   ... and {len(configs) - 5} more")
    
    print(f"\n✅ Total clean entries: {len(all_final)}")
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE - ALL FACTORS NOW CLEAN!")
    print("=" * 70)
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
