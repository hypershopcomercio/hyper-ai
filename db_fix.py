
import sqlite3
import os

DB_FILE = 'hyper_sync.db'

def fix_db():
    if not os.path.exists(DB_FILE):
        print("DB file not found, nothing to fix. It will be created by app.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if 'sku' column exists in 'ads'
    cursor.execute("PRAGMA table_info(ads)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'sku' not in columns:
        print("Adding 'sku' column to 'ads' table...")
        try:
            cursor.execute("ALTER TABLE ads ADD COLUMN sku VARCHAR")
            cursor.execute("CREATE INDEX ix_ads_sku ON ads (sku)")
            conn.commit()
            print("Done.")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("'sku' column already exists.")
        
    conn.close()

if __name__ == "__main__":
    fix_db()
