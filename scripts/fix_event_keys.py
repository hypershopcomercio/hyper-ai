"""
Delete Event entries with numeric keys from CalibrationHistory
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
print("FIXING EVENT FACTOR - DELETE NUMERIC KEYS")
print("=" * 70)

db = SessionLocal()

try:
    # Find event entries with numeric keys
    numeric_keys = ['0', '1', '2', '3', '0.0', '1.0', '2.0', '3.0']
    
    bad_events = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'event',
        CalibrationHistory.fator_chave.in_(numeric_keys)
    ).all()
    
    print(f"\nFound {len(bad_events)} Event entries with numeric keys")
    
    if bad_events:
        print("\nDeleting invalid entries...")
        for event in bad_events:
            logger.info(f"  Deleting event:{event.fator_chave} (ID {event.id})")
            db.delete(event)
        
        db.commit()
        print(f"\n✅ Deleted {len(bad_events)} invalid Event entries")
    else:
        print("\n✅ No invalid Event entries found")
    
    # Show remaining
    remaining = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'event'
    ).count()
    
    print(f"\n✅ Remaining Event CalibrationHistory entries: {remaining}")
    
    # Show sample
    print("\nSample valid entries:")
    valid = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'event'
    ).limit(5).all()
    
    for v in valid:
        print(f"  {v.fator_chave}: {v.valor_novo}")
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
finally:
    db.close()
