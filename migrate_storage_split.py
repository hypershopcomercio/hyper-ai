from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        with conn.begin():
            # Add new columns to product_financial_metrics
            try:
                conn.execute(text("ALTER TABLE product_financial_metrics ADD COLUMN daily_storage_fee NUMERIC(10, 4) DEFAULT 0.0"))
                print("Added daily_storage_fee column")
            except Exception as e:
                print(f"Skipping daily_storage_fee: {e}")

            try:
                conn.execute(text("ALTER TABLE product_financial_metrics ADD COLUMN inbound_freight_cost NUMERIC(10, 2) DEFAULT 0.0"))
                print("Added inbound_freight_cost column")
            except Exception as e:
                print(f"Skipping inbound_freight_cost: {e}")
                
            try:
                conn.execute(text("ALTER TABLE product_financial_metrics ADD COLUMN storage_risk_cost NUMERIC(10, 2) DEFAULT 0.0"))
                print("Added storage_risk_cost column")
            except Exception as e:
                print(f"Skipping storage_risk_cost: {e}")

if __name__ == "__main__":
    migrate()
