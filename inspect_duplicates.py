
import sys
import os
import logging
from sqlalchemy import func, desc

# Setup basic logging
logging.basicConfig(level=logging.INFO)

# Ensure root is in path
sys.path.append(os.getcwd())

try:
    from app.core.database import SessionLocal
    from app.models.forecast_learning import ForecastLog
    
    print("Initializing DB Session...")
    db = SessionLocal()
    
    # Find duplicates by hora_alvo
    # Group by hora_alvo and count
    duplicates = db.query(
        ForecastLog.hora_alvo,
        func.count(ForecastLog.id).label('count')
    ).group_by(
        ForecastLog.hora_alvo
    ).having(
        func.count(ForecastLog.id) > 1
    ).all()
    
    print(f"Found {len(duplicates)} target hours with duplicate logs.")
    
    for dup in duplicates:
        print(f"\n--- Duplicates for {dup.hora_alvo} (Count: {dup.count}) ---")
        # Fetch actual rows
        logs = db.query(ForecastLog).filter(
            ForecastLog.hora_alvo == dup.hora_alvo
        ).order_by(desc(ForecastLog.timestamp_previsao)).all()
        
        for log in logs:
            print(f"ID: {log.id} | Generated: {log.timestamp_previsao} | Predicted: {log.valor_previsto}")
            
    db.close()
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
