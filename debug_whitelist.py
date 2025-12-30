
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.core.database import SessionLocal
from app.models.forecast_learning import AllowedFactor

def check_whitelist():
    db = SessionLocal()
    try:
        factors = db.query(AllowedFactor).filter(AllowedFactor.is_active == 'Y').all()
        print(f"Total Allowed Factors: {len(factors)}")
        
        allowed_map = {}
        for f in factors:
            if f.factor_type not in allowed_map:
                allowed_map[f.factor_type] = []
            allowed_map[f.factor_type].append(f.factor_key)
            
        import json
        print(json.dumps(allowed_map, indent=2))
        
    finally:
        db.close()

if __name__ == "__main__":
    check_whitelist()
