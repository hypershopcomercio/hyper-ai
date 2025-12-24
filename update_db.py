from app.core.database import SessionLocal
from sqlalchemy import text

def add_status_column():
    db = SessionLocal()
    try:
        print("Checking if status column exists in system_logs...")
        # Simple check: try selecting it
        try:
            db.execute(text("SELECT status FROM system_logs LIMIT 1"))
            print("Column 'status' already exists.")
        except Exception:
            print("Column 'status' missing. Adding it...")
            db.rollback()
            db.execute(text("ALTER TABLE system_logs ADD COLUMN status VARCHAR(20)"))
            db.commit()
            print("Column 'status' added successfully.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_status_column()
