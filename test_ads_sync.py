
from app.services.sync_engine import SyncEngine
import logging

logging.basicConfig(level=logging.INFO)

def test_sync_ads():
    print("Testing Ads Spend Sync...")
    engine = SyncEngine()
    try:
        engine.sync_ads_spend()
        print("Sync method executed (check logs forAuth/results).")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sync_ads()
