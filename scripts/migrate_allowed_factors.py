
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, engine, Base
from app.models.forecast_learning import AllowedFactor

# DEFINING INITIAL WHITELIST (FROM FORECAST JOB)
INITIAL_WHITELIST = {
    "day_of_week": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"],
    "momentum": ["up", "down", "neutral", "normal", "default"],
    "period_of_month": ["inicio", "meio", "fim"],
    "seasonal": ["verao", "inverno", "outono", "primavera", "neutro"],
    "payment_day": ["quinto_dia_util", "dia_15", "dia_20", "normal"],
    "week_of_month": ["1", "2", "3", "4", "5"],
}

def migrate_allowed_factors():
    print("=== MIGRATING ALLOWED FACTORS ===")
    
    # 1. Create Table
    print("Creating table allowed_factors...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 2. Check if empty
        count = db.query(AllowedFactor).count()
        if count > 0:
            print(f"Table already has {count} entries. Skipping seed.")
            return

        # 3. Seed Data
        print("Seeding initial whitelist...")
        added_count = 0
        
        for f_type, keys in INITIAL_WHITELIST.items():
            for key in keys:
                # Add descriptions for clarity
                desc = None
                if f_type == "momentum":
                    if key == "up": desc = "Vendas acima do esperado"
                    if key == "down": desc = "Vendas abaixo do esperado"
                
                factor = AllowedFactor(
                    factor_type=f_type,
                    factor_key=key,
                    description=desc
                )
                db.add(factor)
                added_count += 1
        
        db.commit()
        print(f"Successfully seeded {added_count} allowed factors.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_allowed_factors()
