
from app.core.database import SessionLocal, engine
from sqlalchemy import text

def migrate_sales_table():
    with engine.connect() as conn:
        print("Migrating 'sales' table...")
        
        # Helper to add column if not exists
        def add_column(col_name, col_type):
            try:
                conn.execute(text(f"ALTER TABLE sales ADD COLUMN {col_name} {col_type}"))
                print(f"Added column {col_name}")
            except Exception as e:
                # Column likely exists
                print(f"Skipping {col_name} (likely exists or error: {e})")

        add_column("unit_price", "FLOAT DEFAULT 0")
        add_column("shipping_cost", "FLOAT DEFAULT 0")
        add_column("commission_cost", "FLOAT DEFAULT 0")
        add_column("tax_cost", "FLOAT DEFAULT 0")
        add_column("product_cost", "FLOAT DEFAULT 0")
        add_column("marketing_cost", "FLOAT DEFAULT 0")
        add_column("total_cost", "FLOAT DEFAULT 0")
        add_column("net_margin", "FLOAT DEFAULT 0")
        add_column("margin_percent", "FLOAT DEFAULT 0")
        
        conn.commit()
        print("Migration finished.")

if __name__ == "__main__":
    migrate_sales_table()
