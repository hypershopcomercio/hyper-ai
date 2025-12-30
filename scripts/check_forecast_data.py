from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from datetime import datetime, timedelta
from sqlalchemy import func

db = SessionLocal()
try:
    since = datetime.now() - timedelta(days=7)
    
    total = db.query(ForecastLog).filter(ForecastLog.hora_alvo >= since).count()
    reconciled = db.query(ForecastLog).filter(
        ForecastLog.hora_alvo >= since,
        ForecastLog.valor_real.isnot(None)
    ).count()
    
    with_error = db.query(ForecastLog).filter(
        ForecastLog.hora_alvo >= since,
        ForecastLog.erro_percentual.isnot(None)
    ).count()
    
    print(f"Stats for the last 7 days:")
    print(f"Total logs: {total}")
    print(f"Reconciled logs: {reconciled}")
    print(f"Logs with error_percentual: {with_error}")
    
    if reconciled > 0:
        latest = db.query(ForecastLog).filter(ForecastLog.valor_real.isnot(None)).order_by(ForecastLog.hora_alvo.desc()).first()
        print(f"Latest reconciled log: {latest.hora_alvo} (ID: {latest.id})")
    else:
        print("No reconciled logs found in the last 7 days.")
        
finally:
    db.close()
