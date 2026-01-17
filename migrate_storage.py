
from sqlalchemy import text
from app.core.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='product_financial_metrics' AND column_name='storage_cost'"))
        if not result.fetchone():
            print("Adding storage_cost column...")
            db.execute(text("ALTER TABLE product_financial_metrics ADD COLUMN storage_cost NUMERIC(10, 2) DEFAULT 0.0"))
            db.commit()
            print("Migration successful!")
        else:
            print("Column storage_cost already exists.")
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
