
import sys
sys.path.append('.')

from datetime import datetime, timedelta, timezone, date
from sqlalchemy import func, and_
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.models.forecast_learning import ForecastLog
from app.services.forecast.engine import HyperForecast

db = SessionLocal()

# Timezone Brasilia (UTC-3)
tz_br = timezone(timedelta(hours=-3))
now_br = datetime.now(tz_br)
today = now_br.date()
yesterday = today - timedelta(days=1)

print("="*60)
print("RESTAURAÇÃO COMPLETA DOS LOGS DE PREVISÃO")
print("="*60)

# ============================================================
# PARTE 1: RESTAURAR ONTEM (26/12) COM DADOS CORRETOS
# ============================================================
print(f"\n[1/2] RESTAURANDO ONTEM ({yesterday})...")

# Previsões originais do sistema (horas 11-23)
original_predictions = {
    11: 140.60,
    12: 179.12,
    13: 191.35,
    14: 387.57,
    15: 561.72,
    16: 589.58,
    17: 638.78,
    18: 1056.26,
    19: 732.12,
    20: 783.26,
    21: 927.27,
    22: 619.86,
    23: 592.60
}

yesterday_logs = []

for h in range(24):
    # hora_alvo em horário local (Brasília)
    hora_alvo = datetime(yesterday.year, yesterday.month, yesterday.day, h, 0, 0)
    
    # Para buscar vendas reais, converter para UTC
    local_start = datetime(yesterday.year, yesterday.month, yesterday.day, h, 0, 0, tzinfo=tz_br)
    local_end = local_start + timedelta(hours=1)
    utc_start = local_start.astimezone(timezone.utc).replace(tzinfo=None)
    utc_end = local_end.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Buscar vendas reais
    real_revenue = db.query(func.sum(MlOrder.total_amount)).filter(
        MlOrder.date_closed >= utc_start,
        MlOrder.date_closed < utc_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar()
    real_revenue = float(real_revenue or 0)
    
    # Previsão (0 para horas sem previsão original)
    predicted = original_predictions.get(h, 0.0)
    
    # Calcular erro
    if real_revenue > 0 and predicted > 0:
        error = ((predicted - real_revenue) / real_revenue) * 100
    elif predicted > 0:
        error = 100.0
    elif real_revenue > 0:
        error = -100.0
    else:
        error = 0.0
    error = max(-999.99, min(999.99, error))
    
    log = ForecastLog(
        timestamp_previsao=datetime(yesterday.year, yesterday.month, yesterday.day, 13, 9, 40),  # Original timestamp
        hora_alvo=hora_alvo,
        valor_previsto=predicted,
        valor_real=real_revenue,
        erro_percentual=round(error, 2),
        fatores_usados={"restaurado": True},
        modelo_versao="heuristic_v1"
    )
    db.add(log)
    yesterday_logs.append((h, predicted, real_revenue, error))

db.commit()

# Mostrar resumo de ontem
total_pred_yesterday = sum(p for h, p, r, e in yesterday_logs)
total_real_yesterday = sum(r for h, p, r, e in yesterday_logs)
print(f"   ✓ 24 logs criados para {yesterday}")
print(f"   ✓ Total Previsto: R$ {total_pred_yesterday:,.2f}")
print(f"   ✓ Total Realizado: R$ {total_real_yesterday:,.2f}")

# ============================================================
# PARTE 2: GERAR PREVISÕES DE HOJE (27/12) PARA TODAS AS HORAS
# ============================================================
print(f"\n[2/2] GERANDO PREVISÕES DE HOJE ({today})...")

forecast_engine = HyperForecast(db)

today_logs = []
for h in range(24):
    hora_alvo = datetime(today.year, today.month, today.day, h, 0, 0)
    
    # Verificar se já existe log para esta hora
    existing = db.query(ForecastLog).filter(ForecastLog.hora_alvo == hora_alvo).first()
    if existing:
        print(f"   {h:02d}:00 -> Já existe (ID {existing.id})")
        continue
    
    # Gerar previsão usando o engine
    prediction_data = forecast_engine.predict_hour(h, today)
    predicted = prediction_data.get("prediction", 0)
    
    # Para horas já passadas, buscar o valor real
    current_hour = now_br.hour
    if h <= current_hour:
        # Buscar vendas reais (converter para UTC)
        local_start = datetime(today.year, today.month, today.day, h, 0, 0, tzinfo=tz_br)
        local_end = local_start + timedelta(hours=1)
        utc_start = local_start.astimezone(timezone.utc).replace(tzinfo=None)
        utc_end = local_end.astimezone(timezone.utc).replace(tzinfo=None)
        
        real_revenue = db.query(func.sum(MlOrder.total_amount)).filter(
            MlOrder.date_closed >= utc_start,
            MlOrder.date_closed < utc_end,
            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
        ).scalar()
        real_revenue = float(real_revenue or 0)
        
        # Calcular erro
        if real_revenue > 0 and predicted > 0:
            error = ((predicted - real_revenue) / real_revenue) * 100
        elif predicted > 0:
            error = 100.0
        else:
            error = 0.0
        error = max(-999.99, min(999.99, error))
    else:
        # Hora futura - sem valor real ainda
        real_revenue = None
        error = None
    
    log = ForecastLog(
        timestamp_previsao=now_br.replace(tzinfo=None),
        hora_alvo=hora_alvo,
        valor_previsto=round(predicted, 2),
        valor_real=real_revenue,
        erro_percentual=round(error, 2) if error is not None else None,
        fatores_usados=prediction_data.get("factors", {}),
        modelo_versao="heuristic_v1"
    )
    db.add(log)
    
    status = "✓ Reconciliado" if h <= current_hour else "○ Pendente"
    print(f"   {h:02d}:00 -> Prev: R$ {predicted:,.2f} | Real: {'R$ ' + f'{real_revenue:,.2f}' if real_revenue is not None else '-'} | {status}")
    today_logs.append((h, predicted, real_revenue))

db.commit()

# Resumo
total_pred_today = sum(p for h, p, r in today_logs)
total_real_today = sum(r or 0 for h, p, r in today_logs)
print(f"\n   ✓ {len(today_logs)} previsões geradas para {today}")
print(f"   ✓ Total Previsto: R$ {total_pred_today:,.2f}")

db.close()

print("\n" + "="*60)
print("RESTAURAÇÃO CONCLUÍDA!")
print("="*60)
