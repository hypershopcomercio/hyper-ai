import sqlite3
import os

db_path = 'hyper_sync.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, COUNT(*) FROM ml_orders GROUP BY status")
        res = cursor.fetchall()
        print("Status counts:")
        for r in res:
            print(f"- {r[0]}: {r[1]}")
            
        print("\nStatuses for Yesterday (April 28):")
        # Start April 28 03:00 UTC
        cursor.execute("SELECT ml_order_id, status, total_amount, date_created, date_closed FROM ml_orders WHERE date_created >= '2026-04-28 00:00:00'")
        res_yesterday = cursor.fetchall()
        for r in res_yesterday:
             print(f"ID: {r[0]}, Status: {r[1]}, Amount: {r[2]}, Created: {r[3]}, Closed: {r[4]}")
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("No DB")
