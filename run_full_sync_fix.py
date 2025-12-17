
from app.services.sync_engine import SyncEngine
import logging

logging.basicConfig(level=logging.INFO)

def fix_all():
    print("Step 1: Syncing Ads (and Variations now)...")
    engine = SyncEngine()
    try:
        engine.sync_ads() # This now calls _upsert_variations
        print("Ads Sync Done.")
    except Exception as e:
        print(f"Ads Sync Failed: {e}")

    print("\nStep 2: Syncing Costs (Tiny ERP)...")
    try:
        engine.sync_tiny_costs() # Fetches costs for new var SKUs + Bubble up
        print("Costs Sync Done.")
    except Exception as e:
        print(f"Costs Sync Failed: {e}")
        
    print("\nProcess Complete. Check UI for 'Carrinho Jeep' cost.")

if __name__ == "__main__":
    fix_all()
