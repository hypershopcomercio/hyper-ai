
from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("Starting Sprint 2 Migration...")

        # 1. ml_visits
        print("Creating table: ml_visits")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ml_visits (
            id SERIAL PRIMARY KEY,
            item_id VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            visits INTEGER DEFAULT 0,
            source VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(item_id, date)
        );
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_visits_date ON ml_visits(date);"))

        # 2. ml_orders
        print("Creating table: ml_orders")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ml_orders (
            id SERIAL PRIMARY KEY,
            ml_order_id VARCHAR(50) UNIQUE NOT NULL,
            seller_id VARCHAR(50),
            status VARCHAR(50),
            total_amount DECIMAL(12,2),
            paid_amount DECIMAL(12,2),
            currency_id VARCHAR(10),
            buyer_id VARCHAR(50),
            shipping_id VARCHAR(50),
            shipping_cost DECIMAL(10,2),
            date_created TIMESTAMP,
            date_closed TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_date ON ml_orders(date_created);"))

        # 3. ml_order_items
        print("Creating table: ml_order_items")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ml_order_items (
            id SERIAL PRIMARY KEY,
            ml_order_id VARCHAR(50) NOT NULL,
            ml_item_id VARCHAR(50) NOT NULL,
            sku VARCHAR(100),
            title VARCHAR(500),
            quantity INTEGER,
            unit_price DECIMAL(12,2),
            sale_fee DECIMAL(12,2),
            created_at TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY (ml_order_id) REFERENCES ml_orders(ml_order_id)
        );
        """))

        # 4. tiny_stock
        print("Creating table: tiny_stock")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS tiny_stock (
            id SERIAL PRIMARY KEY,
            sku VARCHAR(100) NOT NULL,
            warehouse VARCHAR(100),
            quantity INTEGER DEFAULT 0,
            reserved INTEGER DEFAULT 0,
            available INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT NOW(),
            UNIQUE(sku, warehouse)
        );
        """))

        # 5. ml_metrics_daily
        print("Creating table: ml_metrics_daily")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ml_metrics_daily (
            id SERIAL PRIMARY KEY,
            item_id VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            visits INTEGER DEFAULT 0,
            sales_qty INTEGER DEFAULT 0,
            sales_revenue DECIMAL(12,2) DEFAULT 0,
            conversion_rate DECIMAL(5,2),
            avg_price DECIMAL(12,2),
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(item_id, date)
        );
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_metrics_date ON ml_metrics_daily(date);"))

        # 6. decision_rules
        print("Creating table: decision_rules")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS decision_rules (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            condition_sql TEXT,
            action_type VARCHAR(50),
            priority VARCHAR(20) DEFAULT 'medium',
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """))
        
        # 7. Add columns to tiny_products
        print("Updating table: tiny_products")
        conn.execute(text("ALTER TABLE tiny_products ADD COLUMN IF NOT EXISTS weight DECIMAL(10,3);"))
        conn.execute(text("ALTER TABLE tiny_products ADD COLUMN IF NOT EXISTS width DECIMAL(10,2);"))
        conn.execute(text("ALTER TABLE tiny_products ADD COLUMN IF NOT EXISTS height DECIMAL(10,2);"))
        conn.execute(text("ALTER TABLE tiny_products ADD COLUMN IF NOT EXISTS length DECIMAL(10,2);"))

        conn.commit()
        print("Sprint 2 Migration Completed Successfully.")

if __name__ == "__main__":
    run_migration()
