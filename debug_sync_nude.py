from app.services.sync_engine import SyncEngine
from app.core.database import SessionLocal
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sync_nude():
    print("--- Testing Manual Sync for KIT-CUIDADOS-BEBE-NUDE ---")
    engine = SyncEngine()
    
    sku = 'KIT-CUIDADOS-BEBE-NUDE'
    
    # Call internal method directly
    print(f"Calling _fetch_and_save_tiny('{sku}')...")
    try:
        result = engine._fetch_and_save_tiny(sku)
        
        if result:
            print(f"Result: ID={result.id}, SKU={result.sku}, Name={result.name}, Cost={result.cost}")
        else:
            print("Result: None (Failed to fetch/save)")

        print("Committing changes...")
        engine.db.commit()
    except Exception as e:
        print(f"Error: {e}")
        engine.db.rollback()

    # Check siblings in DB
    print("\nChecking Validation (Siblings in DB):")
    from app.models.tiny_product import TinyProduct
    siblings = engine.db.query(TinyProduct).filter(TinyProduct.sku.ilike('KIT-CUIDADOS%')).all()
    for s in siblings:
        print(f"SKU: {s.sku} | Cost: {s.cost}")

test_sync_nude()
