
import sys
import os
from datetime import datetime

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

def inspect_logs():
    db = SessionLocal()
    try:
        # Check logs for 2025-12-29
        target = datetime(2025, 12, 29).date()
        logs = db.query(ForecastLog).filter(
            ForecastLog.hora_alvo >= datetime.combine(target, datetime.min.time())
        ).order_by(ForecastLog.hora_alvo).all()
        
        print(f"--- LOGS FOR {target} ---")
        print(f"Total: {len(logs)}")
        print(f"{'ID':<5} | {'Hora':<16} | {'Prev':<8} | {'Real':<8} | {'Err%':<8} | {'Calib?':<8} | {'Factors'}")
        print("-" * 100)
        
        for l in logs:
            if l.valor_real is None:
                continue
                
            real_val = str(l.valor_real)
            err_val = str(l.erro_percentual)
            calib = str(l.calibrated)
            print(f"Log {l.id} Factors: {l.fatores_usados}")
        
        reconciled_count = len([l for l in logs if l.valor_real is not None])
        print(f"\nSummary: {reconciled_count}/{len(logs)} logs have real values.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_logs()
