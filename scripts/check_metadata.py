import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from datetime import datetime, timedelta

db = SessionLocal()

recent = db.query(ForecastLog).filter(
    ForecastLog.hora_alvo >= datetime.now() - timedelta(hours=24)
).first()

if recent and recent.fatores_usados:
    print("=== META FACTORS ===")
    fatores = recent.fatores_usados
    for k, v in fatores.items():
        if 'meta' in k or 'momentum' in k:
            print(f"  {k}: {v}")

db.close()
