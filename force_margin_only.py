
from app.core.database import SessionLocal
from app.services.tax_service import TaxService
from app.models.ad import Ad
from app.models.system_config import SystemConfig
from app.services.sync_engine import SyncEngine
from sqlalchemy import and_

print("Starting ISOLATED Margin Update...")
db = SessionLocal()
engine = SyncEngine() # Just for helper methods if needed, but we'll do logic here manually to be safe

try:
    tax_service = TaxService(db_session=db)
    tax_service.update_system_tax_rate()
    
    # Fetch Configurations
    tax_config = db.query(SystemConfig).filter(
        and_(SystemConfig.group == 'geral', SystemConfig.key == "aliquota_simples")
    ).first()
    
    tax_rate = float(tax_config.value) if tax_config and tax_config.value else 12.5
    print(f"Tax Rate: {tax_rate}")
    
    fixed_pkg_config = db.query(SystemConfig).filter(SystemConfig.key == "fixed_packaging_cost").first()
    fixed_pkg = float(fixed_pkg_config.value) if fixed_pkg_config and fixed_pkg_config.value else 0.0
    print(f"Fixed Pkg: {fixed_pkg}")
    
    ads = db.query(Ad).all()
    print(f"Processing {len(ads)} ads (Active + Paused)...")
    
    idx = 0
    for ad in ads:
        engine._process_ad_cost(ad, tax_rate, fixed_pkg)
        idx += 1
        if idx % 50 == 0:
            db.commit()
            print(f"Processed {idx}...")
            
    db.commit()
    print("DONE. All ads updated.")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
