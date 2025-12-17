
print("Checking imports...")
try:
    from app.models.ad import Ad
    from app.models.ad_variation import AdVariation
    from app.services.sync_engine import SyncEngine
    print("Imports Successful.")
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()
