
import sys
import os
from datetime import datetime

# Add project root to path - ROBUSTLY
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.db.base import SessionLocal
from app.models.forecast_learning import ForecastLog

def check_logs():
    db = SessionLocal()
    # Check for 2025-12-29
    target_date = datetime(2025, 12, 29)
    logs = db.query(ForecastLog).filter(ForecastLog.hora_alvo >= target_date).all()
    
    print(f"Found {len(logs)} logs for >= 2025-12-29")
    for log in logs[:10]:
        print(f"ID: {log.id} | Alvo: {log.hora_alvo} | Prev: {log.valor_previsto} | Real: {log.valor_real} | Calib: {log.calibrated}")

if __name__ == "__main__":
    check_logs()
