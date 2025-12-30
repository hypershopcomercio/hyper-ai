"""
Specific fixes for period_of_month, seasonal, event, momentum
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
print("SPECIFIC FIXES: period_of_month, seasonal, event, momentum")
print("=" * 70)

db = SessionLocal()

try:
    # 1. DELETE period_of_month with numeric keys
    print("\n1️⃣ Period of Month: Deleting numeric keys (0.9, 1.0)...")
    
    bad_period = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'period_of_month',
        MultiplierConfig.chave.in_(['0.9', '1.0'])
    ).all()
    
    for p in bad_period:
        logger.info(f"   Deleting period_of_month:{p.chave}")
        db.delete(p)
    
    print(f"   ✅ Deleted {len(bad_period)} entries")
    
    # 2. DELETE seasonal with numeric key
    print("\n2️⃣ Seasonal: Deleting numeric key (1.15)...")
    
    bad_seasonal = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'seasonal',
        MultiplierConfig.chave == '1.15'
    ).all()
    
    for s in bad_seasonal:
        logger.info(f"   Deleting seasonal:{s.chave}")
        db.delete(s)
    
    print(f"   ✅ Deleted {len(bad_seasonal)} entries")
    
    # 3. DELETE event:none (keep event:normal)
    print("\n3️⃣ Event: Deleting 'none' (keeping 'normal')...")
    
    event_none = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'event',
        MultiplierConfig.chave == 'none'
    ).first()
    
    if event_none:
        logger.info(f"   Deleting event:none (valor={event_none.valor})")
        db.delete(event_none)
        print("   ✅ Deleted event:none")
    else:
        print("   ✅ No event:none found")
    
    # 4. MERGE momentum:default into momentum:normal
    print("\n4️⃣ Momentum: Merging 'default' into 'normal'...")
    
    momentum_default = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'momentum',
        MultiplierConfig.chave == 'default'
    ).first()
    
    momentum_normal = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'momentum',
        MultiplierConfig.chave == 'normal'
    ).first()
    
    if momentum_default and momentum_normal:
        # Use the better value (auto-calibrated or higher confidence)
        if momentum_default.calibrado == 'auto' and momentum_normal.calibrado != 'auto':
            logger.info(f"   Using default's value: {momentum_default.valor}")
            momentum_normal.valor = momentum_default.valor
            momentum_normal.calibrado = momentum_default.calibrado
            momentum_normal.confianca = momentum_default.confianca
        elif momentum_default.confianca and momentum_normal.confianca:
            if momentum_default.confianca > momentum_normal.confianca:
                logger.info(f"   Using default's value (higher confidence): {momentum_default.valor}")
                momentum_normal.valor = momentum_default.valor
                momentum_normal.confianca = momentum_default.confianca
        
        logger.info(f"   Deleting momentum:default")
        db.delete(momentum_default)
        print(f"   ✅ Merged: momentum:normal = {momentum_normal.valor}")
    elif momentum_default:
        # Rename default to normal
        logger.info(f"   Renaming default to normal")
        momentum_default.chave = 'normal'
        print(f"   ✅ Renamed: default → normal")
    else:
        print("   ✅ No momentum:default found")
    
    db.commit()
    
    # Show final state
    print("\n" + "=" * 70)
    print("FINAL STATE:")
    print("=" * 70)
    
    print("\n📊 Period of Month:")
    for p in db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'period_of_month').all():
        print(f"   {p.chave}: {p.valor}")
    
    print("\n📊 Seasonal:")
    for s in db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'seasonal').all()[:5]:
        print(f"   {s.chave}: {s.valor}")
    print(f"   ... ({db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'seasonal').count()} total)")
    
    print("\n📊 Event:")
    for e in db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'event').all()[:5]:
        print(f"   {e.chave}: {e.valor}")
    print(f"   ... ({db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'event').count()} total)")
    
    print("\n📊 Momentum:")
    for m in db.query(MultiplierConfig).filter(MultiplierConfig.tipo == 'momentum').all():
        print(f"   {m.chave}: {m.valor}")
    
    print("\n" + "=" * 70)
    print("✅ ALL SPECIFIC FIXES COMPLETE!")
    print("=" * 70)
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
