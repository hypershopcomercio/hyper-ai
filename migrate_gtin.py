
from app.core.database import SessionLocal
from sqlalchemy import text

def add_gtin_column():
    db = SessionLocal()
    try:
        print("Checking if gtin column exists...")
        # Check if column exists
        res = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='ads' AND column_name='gtin'"))
        if res.fetchone():
            print("Column 'gtin' already exists.")
        else:
            print("Adding column 'gtin' to table 'ads'...")
            db.execute(text("ALTER TABLE ads ADD COLUMN gtin VARCHAR"))
            db.commit()
            print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_gtin_column()
