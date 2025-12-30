"""
Delete specific Event entry with key "1.0" from MultiplierConfig
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
print("DELETE EVENT:1.0 FROM MULTIPLIERCONFIG")
print("=" * 70)

db = SessionLocal()

try:
    # Find event:1.0
    bad_event = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'event',
        MultiplierConfig.chave == '1.0'
    ).first()
    
    if bad_event:
        print(f"\n🎯 Found Event:1.0 (ID {bad_event.id}, valor={bad_event.valor})")
        print(f"   Deleting...")
        db.delete(bad_event)
        db.commit()
        print(f"✅ Deleted!")
    else:
        print("\n✅ No Event:1.0 found in MultiplierConfig")
    
    # Check all events
    print("\n📋 All Event entries in MultiplierConfig:")
    all_events = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'event'
    ).all()
    
    for e in all_events:
        print(f"   {e.chave}: {e.valor}")
    
    print(f"\nTotal: {len(all_events)}")
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
finally:
    db.close()
