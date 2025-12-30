import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig, ForecastLog
from sqlalchemy import func

def audit_duplicates():
    db = SessionLocal()
    try:
        print("\n=== AUDITING MultiplierConfig DUPLICATES ===")
        # Count total configs
        total = db.query(MultiplierConfig).count()
        print(f"Total Configs: {total}")
        
        # Check for duplicates (same type and key)
        duplicates = db.query(
            MultiplierConfig.tipo,
            MultiplierConfig.chave,
            func.count(MultiplierConfig.id).label('count')
        ).group_by(
            MultiplierConfig.tipo,
            MultiplierConfig.chave
        ).having(func.count(MultiplierConfig.id) > 1).all()
        
        if not duplicates:
            print("No duplicates found.")
        else:
            print(f"Found {len(duplicates)} sets of duplicates:")
            for tipo, chave, count in duplicates:
                print(f"  - [{tipo}] '{chave}': {count} entries")
                
        print("\n=== AUDITING GARBAGE KEYS IN ForecastLog ===")
        # Check last 50 logs to see what keys are in fatores_usados
        logs = db.query(ForecastLog).filter(ForecastLog.fatores_usados.isnot(None)).order_by(ForecastLog.id.desc()).limit(50).all()
        
        known_bad_keys = set()
        all_keys = set()
        
        for log in logs:
            if not log.fatores_usados:
                continue
            for k, v in log.fatores_usados.items():
                all_keys.add(k)
                # Check if value looks like that long string
                if isinstance(v, str) and "abaixo do esperado" in v:
                    print(f"FOUND SUSPICIOUS VALUE in key '{k}': {v}")
                if isinstance(k, str) and "abaixo do esperado" in k:
                    print(f"FOUND SUSPICIOUS KEY: {k}")

        print("\nALL KEYS FOUND IN LOGS:")
        for k in sorted(all_keys):
            print(f"- {k}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    audit_duplicates()
