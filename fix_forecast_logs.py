
import sys
sys.path.append('.')

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.models.forecast_learning import ForecastLog

db = SessionLocal()

# Define timezone Brasilia (UTC-3)
tz_br = timezone(timedelta(hours=-3))
yesterday_br = datetime.now(tz_br).date() - timedelta(days=1)

print(f"=== CORRIGINDO FORECAST LOGS PARA {yesterday_br} ===\n")

# Delete all existing logs for yesterday
start_hora = datetime(yesterday_br.year, yesterday_br.month, yesterday_br.day, 0, 0, 0)
end_hora = datetime(yesterday_br.year, yesterday_br.month, yesterday_br.day, 23, 59, 59)

deleted = db.query(ForecastLog).filter(
    ForecastLog.hora_alvo >= start_hora,
    ForecastLog.hora_alvo <= end_hora
).delete(synchronize_session=False)
db.commit()
print(f"Deletados {deleted} registros antigos.\n")

# Re-populate with correct data
# For each hour in local time, query orders using CORRECT UTC conversion
for h in range(24):
    # hora_alvo is local time (Brasilia)
    hora_alvo_local = datetime(yesterday_br.year, yesterday_br.month, yesterday_br.day, h, 0, 0)
    
    # Convert to UTC range for query
    # Local 00:00 = UTC 03:00 (same day if before midnight, previous day if after)
    hour_start_local = hora_alvo_local.replace(tzinfo=tz_br)
    hour_end_local = hour_start_local + timedelta(hours=1)
    
    hour_start_utc = hour_start_local.astimezone(timezone.utc).replace(tzinfo=None)
    hour_end_utc = hour_end_local.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Query orders for this UTC range
    revenue = db.query(func.sum(MlOrder.total_amount)).filter(
        MlOrder.date_closed >= hour_start_utc,
        MlOrder.date_closed < hour_end_utc,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar()
    
    revenue = float(revenue or 0)
    
    # Create forecast log entry
    new_log = ForecastLog(
        timestamp_previsao=datetime.now(),
        hora_alvo=hora_alvo_local,  # Store as LOCAL time
        valor_previsto=0,  # No prediction for placeholders
        valor_real=revenue,
        erro_percentual=0 if revenue == 0 else -100,
        fatores_usados={"nota": "Placeholder corrigido com TZ"},
        modelo_versao="placeholder_v2"
    )
    db.add(new_log)
    print(f"{h:02d}:00 (Local) -> UTC {hour_start_utc.strftime('%H:%M')} a {hour_end_utc.strftime('%H:%M')} -> R$ {revenue:,.2f}")

db.commit()

# Verify total
total = db.query(func.sum(ForecastLog.valor_real)).filter(
    ForecastLog.hora_alvo >= start_hora,
    ForecastLog.hora_alvo <= end_hora
).scalar()
print(f"\nNovo Total Realizado: R$ {float(total or 0):,.2f}")

db.close()
print("\n=== CORREÇÃO CONCLUÍDA ===")
