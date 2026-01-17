from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig
from decimal import Decimal

db = SessionLocal()
try:
    print("--- RESETTING SEASONAL MULTIPLIERS ---")
    
    # Update seasonal factors to 1.0
    seasonals = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'seasonal'
    ).all()
    
    for s in seasonals:
        print(f"Resetting {s.chave}: {s.valor} -> 1.0")
        s.valor = Decimal('1.0')
        s.locked = 'Y' # Lock to prevent auto-calibration from messing it up again
        
    db.commit()
    print("Seasonal multipliers reset and locked.")
    
    # Check week_of_month
    weeks = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'week_of_month'
    ).all()
    
    print("\n--- CHECKING WEEK OF MONTH ---")
    for w in weeks:
        print(f"{w.chave}: {w.valor}")
        if float(w.valor) > 1.3:
            print(f"  -> Clamping {w.chave} to 1.2")
            w.valor = Decimal('1.2')
            
    db.commit()
    print("Week of month clamped.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
