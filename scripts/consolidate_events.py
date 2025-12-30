"""
Consolidate duplicate Event:none entries in MultiplierConfig
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
print("CONSOLIDATE DUPLICATE EVENT ENTRIES")
print("=" *70)

db = SessionLocal()

try:
    # Get all Event entries
    all_events = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'event'
    ).all()
    
    # Group by chave
    grouped = {}
    for e in all_events:
        if e.chave not in grouped:
            grouped[e.chave] = []
        grouped[e.chave].append(e)
    
    # Find duplicates
    print("\n📋 Checking for duplicates...")
    
    for key, entries in grouped.items():
        if len(entries) > 1:
            print(f"\n🔍 Found {len(entries)} entries for '{key}':")
            
            # Keep the one with best calibration or most recent
            best = max(entries, key=lambda x: (
                1 if x.calibrado == 'auto' else 0,
                x.confianca or 0,
                x.atualizado_em or x.id
            ))
            
            print(f"   ✅ Keeping ID {best.id}: {best.chave} = {best.valor} ({best.calibrado})")
            
            # Delete others
            for e in entries:
                if e.id != best.id:
                    print(f"   ❌ Deleting ID {e.id}: {e.chave} = {e.valor}")
                    db.delete(e)
    
    db.commit()
    
    # Show final
    print("\n" + "=" * 70)
    print("FINAL EVENT ENTRIES:")
    print("=" * 70)
    
    final = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'event'
    ).all()
    
    for e in final:
        print(f"   {e.chave}: {e.valor}")
    
    print(f"\nTotal: {len(final)}")
    print("\n✅ Consolidation complete!")
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
finally:
    db.close()
