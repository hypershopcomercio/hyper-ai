import sys
import os
import logging
from datetime import datetime
from sqlalchemy import func, text, and_

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

def test_comparison():
    db = SessionLocal()
    try:
        # Simulate value sent by frontend (ISO String with Z)
        start_str = "2025-12-29T03:00:00.000Z"
        
        # This might fail on older python if Z is not supported, or return aware datetime
        try:
            since = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            print(f"Parsed 'since': {since} (tzinfo={since.tzinfo})")
        except ValueError:
            print("Failed to parse ISO string with Z directly")
            return

        # Try to query
        try:
            print("Attempting query...")
            log = db.query(ForecastLog).filter(ForecastLog.hora_alvo >= since).first()
            print("Query success!")
        except Exception as e:
            print(f"Query FAILED: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    test_comparison()
