
from app.core.database import SessionLocal, engine
from sqlalchemy import inspect

def inspect_columns():
    inspector = inspect(engine)
    columns = inspector.get_columns('ml_orders')
    
    print("Columns in ml_orders:")
    found = False
    for c in columns:
        print(f"- {c['name']} ({c['type']})")
        if c['name'] == 'date_closed':
            found = True
            
    if found:
        print("\nCONFIRMED: date_closed EXISTS.")
    else:
        print("\nCONFIRMED: date_closed DOES NOT EXIST.")

if __name__ == "__main__":
    inspect_columns()
