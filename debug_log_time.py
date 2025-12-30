
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

def check_log_time():
    db = SessionLocal()
    try:
        log = db.query(ForecastLog).filter(ForecastLog.id == 664).first()
        print(f"Log ID: {log.id}")
        print(f"Hora Alvo (Raw from DB): {log.hora_alvo}")
    finally:
        db.close()

if __name__ == "__main__":
    check_log_time()
