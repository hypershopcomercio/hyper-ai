
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from sqlalchemy import func

def check_dupes():
    db = SessionLocal()
    print("Checking for duplicates...")
    dupes = db.query(MlOrder.ml_order_id, func.count(MlOrder.id))\
        .group_by(MlOrder.ml_order_id)\
        .having(func.count(MlOrder.id) > 1)\
        .all()
        
    if dupes:
        print(f"FOUND {len(dupes)} DUBLICATES!")
        for d in dupes:
            print(d)
    else:
        print("NO DUPLICATES FOUND. Data Integrity OK.")
        
    db.close()

if __name__ == "__main__":
    check_dupes()
