
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

# Get forecast logs hourly values
print("=== FORECAST LOGS (valor_real por hora) ===")
start_hora = datetime(yesterday_br.year, yesterday_br.month, yesterday_br.day, 0, 0, 0)
end_hora = datetime(yesterday_br.year, yesterday_br.month, yesterday_br.day, 23, 59, 59)

logs = db.query(ForecastLog).filter(
    ForecastLog.hora_alvo >= start_hora,
    ForecastLog.hora_alvo <= end_hora
).order_by(ForecastLog.hora_alvo).all()

forecast_by_hour = {}
for log in logs:
    h = log.hora_alvo.hour
    forecast_by_hour[h] = float(log.valor_real or 0)
    print(f"{h:02d}:00 -> R$ {float(log.valor_real or 0):,.2f}")

print(f"\nTotal Forecast: R$ {sum(forecast_by_hour.values()):,.2f}")

# Get ml_orders hourly values
print("\n=== ML_ORDERS (soma por hora, local time) ===")

# Convert date range to UTC for query
start_local = datetime.combine(yesterday_br, datetime.min.time()).replace(tzinfo=tz_br)
end_local = datetime.combine(yesterday_br, datetime.max.time()).replace(tzinfo=tz_br)
start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)

orders = db.query(MlOrder).filter(
    MlOrder.date_closed >= start_utc,
    MlOrder.date_closed <= end_utc,
    MlOrder.status.in_(['paid', 'shipped', 'delivered'])
).all()

orders_by_hour = {h: 0.0 for h in range(24)}
for o in orders:
    # Convert date_closed to local time
    dt_local = o.date_closed.replace(tzinfo=timezone.utc).astimezone(tz_br)
    h = dt_local.hour
    orders_by_hour[h] += float(o.total_amount or 0)

for h in range(24):
    print(f"{h:02d}:00 -> R$ {orders_by_hour[h]:,.2f}")

print(f"\nTotal Orders: R$ {sum(orders_by_hour.values()):,.2f}")

# Compare differences
print("\n=== DIFERENÇAS POR HORA ===")
total_diff = 0
for h in range(24):
    f_val = forecast_by_hour.get(h, 0)
    o_val = orders_by_hour.get(h, 0)
    diff = f_val - o_val
    if abs(diff) > 0.01:
        print(f"{h:02d}:00 -> Forecast: R$ {f_val:,.2f} | Orders: R$ {o_val:,.2f} | Diff: R$ {diff:,.2f}")
        total_diff += diff

print(f"\nTotal Difference: R$ {total_diff:,.2f}")

db.close()
