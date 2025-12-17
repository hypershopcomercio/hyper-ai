
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig
from app.models.ad import Ad
from app.models.system_log import SystemLog
from sqlalchemy import desc

def debug():
    db = SessionLocal()
    try:
        with open("debug_output.txt", "w", encoding="utf-8") as f:
            try:
                # 1. Check Token
                token = db.query(SystemConfig).filter(SystemConfig.key == "tiny_api_token").first()
                f.write(f"--- Token Status ---\n")
                if token:
                    f.write(f"Key Found: yes\n")
                    f.write(f"Value Length: {len(token.value) if token.value else 0}\n")
                    f.write(f"Value Preview: {token.value[:5]}..." if token.value else "Empty")
                    f.write("\n")
                else:
                    f.write("Token NOT found in DB\n")

                # 2. Check Ads SKU
                total_ads = db.query(Ad).count()
                ads_with_sku = db.query(Ad).filter(Ad.sku != None).count()
                ads_without_sku = total_ads - ads_with_sku
                f.write(f"\n--- Ads Status ---\n")
                f.write(f"Total Ads: {total_ads}\n")
                f.write(f"With SKU: {ads_with_sku}\n")
                f.write(f"Without SKU: {ads_without_sku}\n")
                
                # 3. Check Logs
                f.write(f"\n--- Recent System Logs (Last 10) ---\n")
                logs = db.query(SystemLog).order_by(desc(SystemLog.timestamp)).limit(10).all()
                for log in logs:
                    f.write(f"[{log.level}] {log.module}: {log.message} | {log.details}\n")
            except Exception as e:
                f.write(f"Error inside file write: {e}\n")
                import traceback
                f.write(traceback.format_exc())
    except Exception as e:
        print(f"Error opening file: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug()
