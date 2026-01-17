
from app.core.database import SessionLocal, engine
from sqlalchemy import text

def migrate_manual_video():
    with engine.connect() as conn:
        with conn.begin():
            try:
                # Add manual_video_verified if not exists
                conn.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS manual_video_verified BOOLEAN DEFAULT FALSE"))
                print("Added manual_video_verified column.")
                
            except Exception as e:
                print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_manual_video()
