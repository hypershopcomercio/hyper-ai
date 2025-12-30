
import sys
sys.path.append('.')

from datetime import datetime
from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

db = SessionLocal()

# Original prediction values from the system (captured before deletion)
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

print("=== RESTAURANDO VALORES DE PREVISÃO ===\n")

# Find logs for 2025-12-26
start = datetime(2025, 12, 26, 0, 0, 0)
end = datetime(2025, 12, 26, 23, 59, 59)

logs = db.query(ForecastLog).filter(
    ForecastLog.hora_alvo >= start,
    ForecastLog.hora_alvo <= end
).all()

total_previsto = 0.0
total_real = 0.0

for log in logs:
    hour = log.hora_alvo.hour
    
    if hour in original_predictions:
        log.valor_previsto = original_predictions[hour]
        
        # Recalculate error percentage
        real = float(log.valor_real or 0)
        pred = original_predictions[hour]
        
        if real > 0:
            error = ((pred - real) / real) * 100
        elif pred > 0:
            error = 100.0
        else:
            error = 0.0
        
        # Cap error
        error = max(-999.99, min(999.99, error))
        log.erro_percentual = round(error, 2)
        
        print(f"{hour:02d}:00 -> Previsto: R$ {pred:,.2f} | Real: R$ {real:,.2f} | Erro: {error:.1f}%")
    else:
        # Placeholder hours (00-10) - keep valor_previsto = 0
        print(f"{hour:02d}:00 -> (Sem previsão original)")
    
    total_previsto += float(log.valor_previsto or 0)
    total_real += float(log.valor_real or 0)

db.commit()

print(f"\n=== TOTAIS ===")
print(f"Total Previsto: R$ {total_previsto:,.2f}")
print(f"Total Realizado: R$ {total_real:,.2f}")

# Calculate accuracy
if total_previsto > 0 and total_real > 0:
    diff = abs(total_previsto - total_real)
    accuracy = max(0, 100 - (diff / total_real * 100))
    print(f"Acuracidade: {accuracy:.1f}%")

db.close()
print("\n=== RESTAURAÇÃO CONCLUÍDA ===")
