from app.services.meli_sync import MeliSyncService
import logging

logging.basicConfig(level=logging.INFO)

service = MeliSyncService()
print("Starting Sync...")
result = service.sync_listings()
print(f"Result: {result}")
