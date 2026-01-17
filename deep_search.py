
import logging
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.ad import Ad

def deep_search():
    db = SessionLocal()
    try:
        print("--- DATABASE TABLES ---")
        res = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
        for r in res:
            print(f"[TABLE] {r[0]}")
    finally:
        db.close()

if __name__ == "__main__":
    deep_search()
