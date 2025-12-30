import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker
from app.models.forecast_learning import ForecastLog, CalibrationHistory
from datetime import datetime, timedelta

# Database setup
DATABASE_URL = "postgresql://postgres:gWh28%40dGcMp@localhost:5432/hypershop"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

log_id = 590
print(f"Fetching log {log_id}...")

try:
    log = db.query(ForecastLog).filter(ForecastLog.id == log_id).first()
    
    if not log:
        print("Log not found")
        sys.exit(1)
    
    print(f"Log found: {log}")
    print(f"Timestamp: {log.timestamp_previsao} (type: {type(log.timestamp_previsao)})")
    
    # Simulate the API logic
    now = datetime.now()
    if log.valor_real is not None:
        status = 'high_error' if log.erro_percentual and abs(float(log.erro_percentual)) > 20 else 'reconciled'
    elif log.hora_alvo < now:
        status = 'awaiting'
    else:
        status = 'pending'
    
    print(f"Status: {status}")
    
    # Get calibration info
    print("Checking calibration_impact attribute...")
    calibration_impact = getattr(log, 'calibration_impact', None) or []
    print(f"calibration_impact: {calibration_impact}")
    
    calibrated = getattr(log, 'calibrated', 'N')
    print(f"calibrated: {calibrated}")
    
    if not calibration_impact and log.hora_alvo:
        print("Searching CalibrationHistory...")
        
        # This was the logic in the API
        calibrations = db.query(CalibrationHistory).filter(
            and_(
                CalibrationHistory.data_calibracao >= log.timestamp_previsao,
                CalibrationHistory.data_calibracao <= log.timestamp_previsao + timedelta(hours=24)
            )
        ).all()
        
        print(f"Found {len(calibrations)} calibration history entries")
        
        if calibrations:
            calibration_impact = [
                {
                    "factor_type": c.tipo_fator,
                    "factor_key": c.fator_chave,
                    "old_value": float(c.valor_anterior),
                    "new_value": float(c.valor_novo),
                    "avg_error": float(c.erro_medio),
                    "samples": c.amostras,
                    "timestamp": c.data_calibracao.isoformat()
                }
                for c in calibrations
            ]
            print("Serialized calibration impact successfully")

    # Serialize result like API
    result = {
        "id": log.id,
        "timestamp_previsao": log.timestamp_previsao.isoformat() if log.timestamp_previsao else None,
        "hora_alvo": log.hora_alvo.isoformat() if log.hora_alvo else None,
        "valor_previsto": float(log.valor_previsto) if log.valor_previsto else 0,
        "valor_real": float(log.valor_real) if log.valor_real else None,
        "erro_percentual": float(log.erro_percentual) if log.erro_percentual else None,
        "status": status,
        "baseline_usado": float(log.baseline_usado) if log.baseline_usado else None,
        "modelo_versao": log.modelo_versao,
        "fatores_usados": log.fatores_usados or {},
        "calibrated": calibrated,
        "calibration_impact": calibration_impact
    }
    print("Serialization successful!")
    
    # Check for NaN/Inf in product_mix
    import json
    import math
    
    def check_nan(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                check_nan(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                check_nan(v, f"{path}[{i}]")
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                print(f"WARNING: Found NaN/Inf at {path}: {obj}")
    
    check_nan(result)
    
    # Try actual dumping
    try:
        json_str = json.dumps(result)
        print("JSON Dump successful (length: {})".format(len(json_str)))
    except Exception as e:
        print(f"JSON Dump FAILED: {e}")
        
    # Print product mix keys specifically
    if '_product_mix' in log.fatores_usados:
        pm = log.fatores_usados['_product_mix']
        print(f"Product mix has {len(pm)} items")
        if len(pm) > 0:
            print("First item keys:", pm[0].keys())

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
