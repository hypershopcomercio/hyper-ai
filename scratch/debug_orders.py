
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timedelta
from sqlalchemy import func

def check_orders():
    db = SessionLocal()
    try:
        # Check last 48 hours
        cutoff = datetime.now() - timedelta(hours=48)
        orders = db.query(MlOrder).filter(MlOrder.date_created >= cutoff).all()
        
        print(f"--- Diagnóstico de Pedidos (Últimas 48h) ---")
        print(f"Total de pedidos encontrados: {len(orders)}")
        
        status_counts = db.query(MlOrder.status, func.count(MlOrder.id)).filter(MlOrder.date_created >= cutoff).group_by(MlOrder.status).all()
        for status, count in status_counts:
            print(f"Status '{status}': {count} pedidos")
            
        if orders:
            print("\nÚltimos 3 pedidos:")
            for o in orders[:3]:
                print(f"ID: {o.ml_order_id} | Data: {o.date_created} | Status: {o.status} | Valor: {o.total_amount}")
        
        # Check if they are being aggregated
        from app.models.ml_metrics_daily import MlMetricsDaily
        metrics = db.query(MlMetricsDaily).filter(MlMetricsDaily.date >= cutoff.date()).all()
        print(f"\nRegistros em MlMetricsDaily (Desde ontem): {len(metrics)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_orders()
