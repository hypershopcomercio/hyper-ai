
from app.core.database import SessionLocal, engine
from sqlalchemy import text

def migrate_promo_price():
    with engine.connect() as conn:
        with conn.begin():
            try:
                # Add promotion_price if not exists
                conn.execute(text("ALTER TABLE ads ADD COLUMN IF NOT EXISTS promotion_price DOUBLE PRECISION"))
                print("Added promotion_price column.")
                
            except Exception as e:
                print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_promo_price()
