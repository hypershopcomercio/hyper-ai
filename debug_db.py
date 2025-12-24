import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
from app.models.system_log import SystemLog
from app.models.system_config import SystemConfig
from sqlalchemy import desc

def debug_check():
    db = SessionLocal()
    try:
        print("=== DEBUG CHECK ===")
        
        # 1. Check ML Token
        token = db.query(OAuthToken).filter_by(provider="mercadolivre").first()
        if token:
            print(f"[ML] Token found. SellerID: {token.seller_id}")
            print(f"[ML] Expires at: {token.expires_at}")
            
            # Check expiry
            if token.expires_at:
                now_aware = datetime.now(token.expires_at.tzinfo)
                if token.expires_at < now_aware:
                    print(f"[ML] CRITICAL: Token EXPIRED! (Now: {now_aware})")
                else:
                    print(f"[ML] Token Valid.")
            else:
                print(f"[ML] No expiration date set.")
                
        else:
            print("[ML] CRITICAL: No OAuth Token found!")

        # 2. Check Recent Logs (last 5)
        print("\n--- Recent System Logs ---")
        logs = db.query(SystemLog).order_by(desc(SystemLog.timestamp)).limit(10).all()
        for l in logs:
            print(f"[{l.timestamp}] {l.module} ({l.level}): {l.message}")
            if l.level == 'ERROR':
                 print(f"   Details: {l.details}")
                 
        # 3. Check Tiny Config
        tiny = db.query(SystemConfig).filter_by(key="TINY_API_TOKEN").first()
        print(f"\n[Tiny] Token: {'Found' if tiny and tiny.value else 'Missing'}")
                 
        # 4. Test Log Insertion
        print("\n[Test] Attempting to insert a test log...")
        try:
            test_log = SystemLog(
                module='debug_test',
                level='INFO',
                message='Test log from debug script',
                # timestamp omitted to test default
            )
            db.add(test_log)
            db.commit()
            print("[Test] Log insertion SUCCESS.")
        except Exception as log_e:
            print(f"[Test] Log insertion FAILED: {log_e}")
            db.rollback()
                 
    except Exception as e:
        print(f"Debug failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_check()
