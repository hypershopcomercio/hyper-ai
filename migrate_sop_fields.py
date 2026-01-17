
from app.core.database import SessionLocal, engine
from sqlalchemy import text

def migrate_db():
    with engine.connect() as conn:
        with conn.begin():
            try:
                # Add video_id if not exists
                conn.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS video_id VARCHAR"))
                print("Added video_id column.")
                
                # Add short_description if not exists
                conn.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS short_description VARCHAR"))
                print("Added short_description column.")
                
            except Exception as e:
                print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_db()
