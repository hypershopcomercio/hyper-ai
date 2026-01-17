
from sqlalchemy import text
from app.core.database import SessionLocal

def search_logs():
    db = SessionLocal()
    try:
        print("--- SEARCHING FORECAST_LOGS ---")
        # Check available columns first
        try:
             res = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='forecast_logs'")).fetchall()
             print([r[0] for r in res])
             
             # Assuming 'mlb_id' or similar exists. Let's check data by ID if column exists.
             # Wait, I don't know the foreign key name.
             # Let's just list 5 rows to see structure
             res = db.execute(text("SELECT * FROM forecast_logs LIMIT 5")).fetchall()
             print(res)
             
        except Exception as e:
             print(f"Log check failed: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    search_logs()
