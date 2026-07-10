import sys
import os

# Ensure app path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal, engine
from sqlalchemy import text

def check_schema():
    with engine.connect() as conn:
        print("=== DESCRIBE nfe_items ===")
        res = conn.execute(text("DESCRIBE nfe_items"))
        for r in res: print(r)
        
        print("\n=== DESCRIBE nfe_imports ===")
        res = conn.execute(text("DESCRIBE nfe_imports"))
        for r in res: print(r)
        
        print("\n=== DESCRIBE nfe_reconciliations ===")
        res = conn.execute(text("DESCRIBE nfe_reconciliations"))
        for r in res: print(r)
        
        print("\n=== SELECT DISTINCT status FROM nfe_imports ===")
        res = conn.execute(text("SELECT DISTINCT status FROM nfe_imports"))
        for r in res: print(r)
        
        print("\n=== SELECT DISTINCT link_status FROM nfe_items ===")
        res = conn.execute(text("SELECT DISTINCT link_status FROM nfe_items"))
        for r in res: print(r)
        
        print("\n=== SELECT * FROM nfe_reconciliations WHERE nfe_id = 1 ===")
        res = conn.execute(text("SELECT * FROM nfe_reconciliations WHERE nfe_id = 1"))
        for r in res: print(r)

if __name__ == "__main__":
    check_schema()
