
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
now_br = datetime.now(tz_br)
today_br = now_br.date()
yesterday_br = today_br - timedelta(days=1)

print(f"=== COMPARAÇÃO DE DADOS: ONTEM ({yesterday_br}) ===\n")

# 1. HYPER AI - soma de forecast_logs.valor_real
# Filter logs for yesterday
# hora_alvo is datetime, so we filter for the whole day
start_hora_alvo = datetime(yesterday_br.year, yesterday_br.month, yesterday_br.day, 0, 0, 0)
end_hora_alvo = datetime(yesterday_br.year, yesterday_br.month, yesterday_br.day, 23, 59, 59)

forecast_total = db.query(func.sum(ForecastLog.valor_real)).filter(
    ForecastLog.hora_alvo >= start_hora_alvo,
    ForecastLog.hora_alvo <= end_hora_alvo
).scalar()
forecast_total = float(forecast_total or 0)
print(f"[HYPER AI]  Total Realizado (forecast_logs.valor_real): R$ {forecast_total:,.2f}")

# Count logs
forecast_count = db.query(ForecastLog).filter(
    ForecastLog.hora_alvo >= start_hora_alvo,
    ForecastLog.hora_alvo <= end_hora_alvo
).count()
print(f"            Entradas de hora: {forecast_count}")

# 2. DASHBOARD - soma de ml_orders.total_amount
# Dashboard uses date_closed with UTC conversion
start_local = datetime.combine(yesterday_br, datetime.min.time()).replace(tzinfo=tz_br)
end_local = datetime.combine(yesterday_br, datetime.max.time()).replace(tzinfo=tz_br)

# Convert to UTC for query (database stores in UTC)
start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)

print(f"\n[DEBUG]     Start UTC: {start_utc}")
print(f"            End UTC: {end_utc}")

# Query same way dashboard does
dashboard_total = db.query(func.sum(MlOrder.total_amount)).filter(
    MlOrder.date_closed >= start_utc,
    MlOrder.date_closed <= end_utc,
    MlOrder.status != 'cancelled'
).scalar()
dashboard_total = float(dashboard_total or 0)
print(f"\n[DASHBOARD] Total Vendas (ml_orders.total_amount, excl cancelled): R$ {dashboard_total:,.2f}")

# Count orders
dashboard_count = db.query(MlOrder).filter(
    MlOrder.date_closed >= start_utc,
    MlOrder.date_closed <= end_utc,
    MlOrder.status != 'cancelled'
).count()
print(f"            Número de pedidos: {dashboard_count}")

# 3. Without status filter
dashboard_total_all = db.query(func.sum(MlOrder.total_amount)).filter(
    MlOrder.date_closed >= start_utc,
    MlOrder.date_closed <= end_utc
).scalar()
dashboard_total_all = float(dashboard_total_all or 0)
print(f"\n[ALL]       Total com TODOS status: R$ {dashboard_total_all:,.2f}")

# 4. With specific status filter (matching cleanup script)
dashboard_total_specific = db.query(func.sum(MlOrder.total_amount)).filter(
    MlOrder.date_closed >= start_utc,
    MlOrder.date_closed <= end_utc,
    MlOrder.status.in_(['paid', 'shipped', 'delivered'])
).scalar()
dashboard_total_specific = float(dashboard_total_specific or 0)
print(f"[SPECIFIC]  Total com status paid/shipped/delivered: R$ {dashboard_total_specific:,.2f}")

print(f"\n=== DIFERENÇAS ===")
print(f"Hyper AI - Dashboard (excl cancelled): R$ {forecast_total - dashboard_total:,.2f}")
print(f"Hyper AI - Dashboard (specific status): R$ {forecast_total - dashboard_total_specific:,.2f}")

db.close()
