
from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # 1. Update 'ads' table with missing columns
        print("Migrating 'ads' table...")
        
        # Add columns if not exist
        # Columns: health (float), shipping_mode (str), attributes (jsonb), pictures (jsonb), 
        # listing_type (str - check exist), commission_percent (float), thumbnail (str), permalink (str)
        # Check existing first avoids errors, but 'ADD COLUMN IF NOT EXISTS' is PG 9.6+ (safe)
        
        queries = [
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS health DECIMAL(5,2);",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS shipping_mode VARCHAR(50);",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS attributes JSONB;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS pictures JSONB;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS thumbnail TEXT;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS permalink TEXT;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS original_price DECIMAL(12,2);",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS listing_type VARCHAR(50);",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS category_name VARCHAR(200);",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS sold_quantity INTEGER DEFAULT 0;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS available_quantity INTEGER DEFAULT 0;",
             # Re-verify commission_percent presence
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS commission_percent DECIMAL(5,2);",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS visits_30d INTEGER DEFAULT 0;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS sales_30d INTEGER DEFAULT 0;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS stock_tiny INTEGER DEFAULT 0;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS stock_divergence INTEGER DEFAULT 0;",
            "ALTER TABLE ads ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP;"
        ]

        for q in queries:
            try:
                conn.execute(text(q))
                print(f"Executed: {q}")
            except Exception as e:
                print(f"Warning/Error on query '{q}': {e}")

        # 2. Create 'sync_logs' table
        print("Creating 'sync_logs' table...")
        create_sync_logs = """
        CREATE TABLE IF NOT EXISTS sync_logs (
            id SERIAL PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL,
            records_processed INTEGER DEFAULT 0,
            records_success INTEGER DEFAULT 0,
            records_error INTEGER DEFAULT 0,
            duration_ms INTEGER,
            error_message TEXT,
            details JSONB,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        conn.execute(text(create_sync_logs))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sync_logs_type ON sync_logs(type);"))
        
        conn.commit()
        print("Migration completed.")

if __name__ == "__main__":
    run_migration()
