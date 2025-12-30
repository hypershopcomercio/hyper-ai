import sys
import os
import logging
from sqlalchemy import func, text, case

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_logs():
    db = SessionLocal()
    try:
        # Count logs by date and status
        # Using case to count reconciled vs error
        reconciled_expr = case(
            (ForecastLog.valor_real != None, 1),
            else_=0
        )
        
        error_expr = case(
            (ForecastLog.erro_percentual != None, 1),
            else_=0
        )

        results = db.query(
            func.date(ForecastLog.hora_alvo).label('date'),
            func.count(ForecastLog.id).label('total'),
            func.sum(reconciled_expr).label('reconciled'),
            func.sum(error_expr).label('with_error')
        ).group_by(func.date(ForecastLog.hora_alvo)).order_by(func.date(ForecastLog.hora_alvo)).all()
        
        print(f"{'DATE':<12} | {'TOTAL':<8} | {'RECONCILED':<10} | {'WITH_ERROR':<10}")
        print("-" * 50)
        
        for r in results:
            print(f"{str(r.date):<12} | {r.total:<8} | {r.reconciled:<10} | {r.with_error:<10}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_logs()
