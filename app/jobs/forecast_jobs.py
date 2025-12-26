"""
Hyper Forecast - Learning Jobs
Daily reconciliation and weekly auto-calibration jobs for the learning system
"""
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog, CalibrationHistory, MultiplierConfig
from app.models.ml_order import MlOrder

logger = logging.getLogger(__name__)


def run_daily_reconciliation():
    """
    Daily job - runs at 03:00
    
    Compares yesterday's predictions with actual sales.
    Updates forecast_logs with valor_real and erro_percentual.
    """
    logger.info("[FORECAST-JOB] Starting daily reconciliation...")
    
    db = SessionLocal()
    
    try:
        # Get yesterday's date
        yesterday = datetime.now().date() - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        
        # Find all forecast logs for yesterday that haven't been reconciled
        pending_logs = db.query(ForecastLog).filter(
            and_(
                ForecastLog.hora_alvo >= yesterday_start,
                ForecastLog.hora_alvo <= yesterday_end,
                ForecastLog.valor_real.is_(None)
            )
        ).all()
        
        if not pending_logs:
            logger.info("[FORECAST-JOB] No pending logs to reconcile for yesterday")
            return {"status": "ok", "reconciled": 0}
        
        logger.info(f"[FORECAST-JOB] Found {len(pending_logs)} logs to reconcile")
        
        reconciled_count = 0
        
        for log in pending_logs:
            # Get actual sales for that hour
            hour_start = log.hora_alvo
            hour_end = hour_start + timedelta(hours=1)
            
            actual_revenue = db.query(func.sum(MlOrder.total_amount)).filter(
                and_(
                    MlOrder.date_closed >= hour_start,
                    MlOrder.date_closed < hour_end,
                    MlOrder.status.in_(['paid', 'shipped', 'delivered'])
                )
            ).scalar()
            
            actual_revenue = float(actual_revenue or 0)
            predicted = float(log.valor_previsto or 0)
            
            # Calculate error percentage
            if actual_revenue > 0:
                erro = ((predicted - actual_revenue) / actual_revenue) * 100
            else:
                # If no actual sales, check if we predicted none
                erro = 0 if predicted == 0 else 100  # 100% error if we predicted sales but got none
            
            # Update the log
            log.valor_real = Decimal(str(round(actual_revenue, 2)))
            log.erro_percentual = Decimal(str(round(erro, 2)))
            
            reconciled_count += 1
            logger.debug(f"[FORECAST-JOB] {log.hora_alvo}: prev={predicted:.2f} real={actual_revenue:.2f} erro={erro:.1f}%")
        
        db.commit()
        logger.info(f"[FORECAST-JOB] Reconciliation complete: {reconciled_count} logs updated")
        
        return {
            "status": "ok", 
            "reconciled": reconciled_count,
            "date": yesterday.isoformat()
        }
        
    except Exception as e:
        logger.error(f"[FORECAST-JOB] Reconciliation failed: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


def run_weekly_calibration():
    """
    Weekly job - runs Sunday 04:00
    
    Analyzes error patterns from the past week.
    Adjusts multipliers that are consistently over/under estimating.
    Saves changes to calibration_history for audit.
    """
    logger.info("[FORECAST-JOB] Starting weekly calibration...")
    
    db = SessionLocal()
    
    try:
        # Get logs from the past 7 days that have been reconciled
        week_ago = datetime.now() - timedelta(days=7)
        
        logs = db.query(ForecastLog).filter(
            and_(
                ForecastLog.timestamp_previsao >= week_ago,
                ForecastLog.valor_real.isnot(None),
                ForecastLog.erro_percentual.isnot(None)
            )
        ).all()
        
        if len(logs) < 50:  # Need minimum samples for meaningful calibration
            logger.info(f"[FORECAST-JOB] Not enough samples for calibration ({len(logs)} < 50)")
            return {"status": "skipped", "reason": "insufficient_samples", "samples": len(logs)}
        
        logger.info(f"[FORECAST-JOB] Analyzing {len(logs)} predictions...")
        
        # Group errors by factor type
        factor_errors = _analyze_errors_by_factor(logs)
        
        # Apply calibration adjustments
        adjustments_made = []
        
        for factor_type, factor_data in factor_errors.items():
            for factor_key, stats in factor_data.items():
                avg_error = stats["avg_error"]
                sample_count = stats["count"]
                
                # Skip if not enough samples for this specific factor
                if sample_count < 10:
                    continue
                
                # Check if error exceeds threshold (±5%)
                if abs(avg_error) > 5:
                    adjustment = _apply_calibration(
                        db, factor_type, factor_key, avg_error, sample_count
                    )
                    if adjustment:
                        adjustments_made.append(adjustment)
        
        db.commit()
        
        logger.info(f"[FORECAST-JOB] Calibration complete: {len(adjustments_made)} adjustments made")
        
        return {
            "status": "ok",
            "total_samples": len(logs),
            "adjustments": adjustments_made
        }
        
    except Exception as e:
        logger.error(f"[FORECAST-JOB] Calibration failed: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


def _analyze_errors_by_factor(logs: List[ForecastLog]) -> Dict:
    """
    Group prediction errors by factor type to identify patterns
    """
    factor_errors = {
        "day_of_week": {},
        "momentum": {},
        "period_of_month": {},
        "event": {},
        "seasonal": {}
    }
    
    for log in logs:
        fatores = log.fatores_usados or {}
        erro = float(log.erro_percentual or 0)
        
        for factor_type, factor_value in fatores.items():
            if factor_type not in factor_errors:
                continue
            
            # Create a key based on factor value (rounded for grouping)
            if isinstance(factor_value, (int, float)):
                key = str(round(factor_value, 2))
            else:
                key = str(factor_value)
            
            if key not in factor_errors[factor_type]:
                factor_errors[factor_type][key] = {"errors": [], "count": 0}
            
            factor_errors[factor_type][key]["errors"].append(erro)
            factor_errors[factor_type][key]["count"] += 1
    
    # Calculate averages
    for factor_type in factor_errors:
        for key in factor_errors[factor_type]:
            errors = factor_errors[factor_type][key]["errors"]
            factor_errors[factor_type][key]["avg_error"] = sum(errors) / len(errors) if errors else 0
            del factor_errors[factor_type][key]["errors"]  # Clean up
    
    return factor_errors


def _apply_calibration(
    db: Session,
    factor_type: str,
    factor_key: str,
    avg_error: float,
    sample_count: int
) -> Dict:
    """
    Apply a calibration adjustment to a multiplier
    """
    # Get current multiplier value from config (or default to 1.0)
    config = db.query(MultiplierConfig).filter(
        and_(
            MultiplierConfig.tipo == factor_type,
            MultiplierConfig.chave == factor_key
        )
    ).first()
    
    old_value = float(config.valor) if config else 1.0
    
    # Calculate adjustment
    # If avg_error is positive (we overestimated), reduce multiplier
    # If avg_error is negative (we underestimated), increase multiplier
    adjustment_factor = 0.02  # 2% adjustment per calibration
    
    if avg_error > 5:
        new_value = old_value * (1 - adjustment_factor)
    elif avg_error < -5:
        new_value = old_value * (1 + adjustment_factor)
    else:
        return None  # No adjustment needed
    
    # Clamp to reasonable range
    new_value = max(0.5, min(2.0, new_value))
    
    # Update or create config
    if config:
        config.valor = Decimal(str(round(new_value, 3)))
        config.calibrado = 'auto'
        config.confianca = min(100, sample_count)
    else:
        config = MultiplierConfig(
            tipo=factor_type,
            chave=factor_key,
            valor=Decimal(str(round(new_value, 3))),
            calibrado='auto',
            confianca=min(100, sample_count)
        )
        db.add(config)
    
    # Record in calibration history
    history = CalibrationHistory(
        data_calibracao=datetime.utcnow(),
        tipo_fator=factor_type,
        fator_chave=factor_key,
        valor_anterior=Decimal(str(round(old_value, 3))),
        valor_novo=Decimal(str(round(new_value, 3))),
        erro_medio=Decimal(str(round(avg_error, 2))),
        amostras=sample_count,
        ajuste_percentual=Decimal(str(round((new_value / old_value - 1) * 100, 2))),
        notas=f"Auto-calibration: avg_error={avg_error:.1f}% samples={sample_count}"
    )
    db.add(history)
    
    logger.info(f"[FORECAST-JOB] Calibrated {factor_type}.{factor_key}: {old_value:.3f} -> {new_value:.3f} (error={avg_error:.1f}%)")
    
    return {
        "factor_type": factor_type,
        "factor_key": factor_key,
        "old_value": old_value,
        "new_value": round(new_value, 3),
        "avg_error": round(avg_error, 1),
        "samples": sample_count
    }


# API endpoint helpers
def get_calibration_status() -> Dict:
    """Get current calibration status and recent history"""
    db = SessionLocal()
    
    try:
        # Count forecast logs
        total_logs = db.query(ForecastLog).count()
        reconciled_logs = db.query(ForecastLog).filter(
            ForecastLog.valor_real.isnot(None)
        ).count()
        
        # Get average error from last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_logs = db.query(ForecastLog).filter(
            and_(
                ForecastLog.timestamp_previsao >= week_ago,
                ForecastLog.erro_percentual.isnot(None)
            )
        ).all()
        
        avg_error = 0
        if recent_logs:
            avg_error = sum(float(l.erro_percentual or 0) for l in recent_logs) / len(recent_logs)
        
        # Get recent calibrations
        recent_calibrations = db.query(CalibrationHistory).order_by(
            CalibrationHistory.data_calibracao.desc()
        ).limit(10).all()
        
        # Get current multiplier configs
        configs = db.query(MultiplierConfig).all()
        
        return {
            "total_predictions_logged": total_logs,
            "predictions_reconciled": reconciled_logs,
            "pending_reconciliation": total_logs - reconciled_logs,
            "avg_error_7d": round(avg_error, 2),
            "recent_calibrations": [
                {
                    "date": c.data_calibracao.isoformat(),
                    "factor": f"{c.tipo_fator}.{c.fator_chave}",
                    "change": f"{c.valor_anterior} -> {c.valor_novo}",
                    "error": float(c.erro_medio)
                } for c in recent_calibrations
            ],
            "current_multipliers": [
                {
                    "type": c.tipo,
                    "key": c.chave,
                    "value": float(c.valor),
                    "source": c.calibrado,
                    "confidence": c.confianca
                } for c in configs
            ]
        }
        
    finally:
        db.close()
