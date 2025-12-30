
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import func, desc

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

print("=== FORECAST LOGS CLEANUP ===")
db = SessionLocal()

# 1. FIND AND DELETE ALL DUPLICATES (keep newest by ID for each hora_alvo)
print("\n1. Finding duplicates...")
duplicates = db.query(
    ForecastLog.hora_alvo,
    func.count(ForecastLog.id).label('count')
).group_by(ForecastLog.hora_alvo).having(func.count(ForecastLog.id) > 1).all()

ids_to_delete = []
for dup in duplicates:
    logs = db.query(ForecastLog).filter(
        ForecastLog.hora_alvo == dup.hora_alvo
    ).order_by(desc(ForecastLog.id)).all()
    # Keep newest (first), delete rest
    for log in logs[1:]:
        ids_to_delete.append(log.id)

if ids_to_delete:
    print(f"   Deleting {len(ids_to_delete)} duplicates: {ids_to_delete}")
    db.query(ForecastLog).filter(ForecastLog.id.in_(ids_to_delete)).delete(synchronize_session=False)
    db.commit()
else:
    print("   No duplicates found.")

# 2. FILL MISSING HOURS FOR 26/12
print("\n2. Filling missing hours for 2025-12-26...")
target_date = datetime(2025, 12, 26)

# Get data from actual sales for the day to fill valor_real
from app.models.ml_order import MlOrder
from sqlalchemy import and_

for hour in range(24):
    target_hour = target_date.replace(hour=hour)
    
    # Check if entry exists
    existing = db.query(ForecastLog).filter(ForecastLog.hora_alvo == target_hour).first()
    
    if not existing:
        # Get actual sales for this hour
        hour_start = target_hour
        hour_end = target_hour + timedelta(hours=1)
        
        actual_revenue = db.query(func.sum(MlOrder.total_amount)).filter(
            and_(
                MlOrder.date_closed >= hour_start,
                MlOrder.date_closed < hour_end,
                MlOrder.status.in_(['paid', 'shipped', 'delivered'])
            )
        ).scalar()
        
        actual_revenue = float(actual_revenue) if actual_revenue else 0.0
        
        # Create placeholder entry (no prediction, but has real value)
        new_log = ForecastLog(
            timestamp_previsao=datetime.now(),  # When we created this placeholder
            hora_alvo=target_hour,
            valor_previsto=0,  # No prediction was made
            valor_real=actual_revenue,
            erro_percentual=0 if actual_revenue == 0 else -100,  # -100% means we predicted 0
            fatores_usados={"nota": "Placeholder - sem previsão original"},
            modelo_versao="placeholder_v1"
        )
        db.add(new_log)
        print(f"   Added placeholder for {hour:02d}:00 (Real: R$ {actual_revenue:.2f})")

db.commit()

# 3. DELETE OLD ENTRIES (25/12) - keep only 26/12
print("\n3. Removing old entries from 25/12...")
old_logs = db.query(ForecastLog).filter(
    ForecastLog.hora_alvo < datetime(2025, 12, 26)
).all()

if old_logs:
    old_ids = [l.id for l in old_logs]
    print(f"   Deleting {len(old_ids)} old entries: {old_ids}")
    db.query(ForecastLog).filter(ForecastLog.id.in_(old_ids)).delete(synchronize_session=False)
    db.commit()
else:
    print("   No old entries found.")

# 4. FINAL VERIFICATION
print("\n4. Final state (ordered by hora_alvo):")
final_logs = db.query(ForecastLog).order_by(ForecastLog.hora_alvo).all()
total_previsto = 0
total_real = 0
for log in final_logs:
    previsto = float(log.valor_previsto or 0)
    real = float(log.valor_real or 0)
    total_previsto += previsto
    total_real += real
    status = "✓" if previsto > 0 else "○"
    print(f"   {status} {log.hora_alvo.strftime('%d/%m %H:00')} | Prev: R$ {previsto:,.2f} | Real: R$ {real:,.2f}")

print(f"\n   TOTAL: Previsto R$ {total_previsto:,.2f} | Real R$ {total_real:,.2f}")
print(f"   Entries: {len(final_logs)}")

db.close()
print("\n=== CLEANUP COMPLETE ===")
