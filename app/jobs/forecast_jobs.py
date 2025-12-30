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
from app.models.forecast_learning import ForecastLog, CalibrationHistory, MultiplierConfig, AllowedFactor
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.system_log import SystemLog
import json

logger = logging.getLogger(__name__)


def run_daily_predictions(manual_run=False):
    """
    Daily job - runs at 00:00 (midnight) OR manually
    Generate predictions for the next 24 hours (or entire days if manual).
    
    Args:
        manual_run: If True, generates for ALL hours of today + tomorrow (48 total)
                   If False (scheduled), generates only for tomorrow's 24 hours
    """
    logger.info("[FORECAST-JOB] Starting daily prediction generation...")
    
    db = SessionLocal()
    
    try:
        from app.services.forecast.engine import HyperForecast
        from datetime import datetime, timedelta
        
        forecast = HyperForecast(db)
        now = datetime.now()
        
        predictions_made = 0
        target_hours = []
        
        if manual_run:
            # MANUAL: Generate for ALL hours of today (00-23) + ALL hours of tomorrow (00-23)
            logger.info("[FORECAST-JOB] MANUAL RUN: Generating for TODAY + TOMORROW (48 hours total)")
            
            today = now.date()
            tomorrow = today + timedelta(days=1)
            
            # Add ALL 24 hours of today (regardless of current time)
            for hour in range(24):
                target_hours.append(datetime.combine(today, datetime.min.time()) + timedelta(hours=hour))
            
            # Add ALL 24 hours of next day
            for hour in range(24):
                target_hours.append(datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=hour))
                
            logger.info(f"[FORECAST-JOB] Target: {len(target_hours)} hours (today 00-23 + tomorrow 00-23)")
        else:
            # SCHEDULED: Only generate for next day's 24 hours
            logger.info("[FORECAST-JOB] SCHEDULED RUN: Generating for TOMORROW only (24 hours)")
            
            tomorrow = now.date() + timedelta(days=1)
            
            # Add all 24 hours of next day
            for hour in range(24):
                target_hours.append(datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=hour))
            
            logger.info(f"[FORECAST-JOB] Target: 24 hours for {tomorrow}")
        
        # Generate predictions for all target hours
        for target_dt in target_hours:
            try:
                # Check if prediction already exists
                existing = db.query(ForecastLog).filter(
                    ForecastLog.hora_alvo == target_dt
                ).first()
                
                if existing:
                    logger.debug(f"[FORECAST-JOB] Skipping {target_dt.strftime('%Y-%m-%d %Hh')} - already exists")
                    continue
                
                # Generate prediction (using hour and date separately)
                hour_num = target_dt.hour
                date_part = target_dt.date()
                
                result = forecast.predict_hour_with_logging(hour_num, date_part)
                
                if result and 'prediction' in result:
                    predictions_made += 1
                    logger.info(f"[FORECAST-JOB] {target_dt.strftime('%Y-%m-%d %Hh')}: R$ {result['prediction']:.2f}")
                
            except Exception as e_hour:
                logger.error(f"[FORECAST-JOB] Failed for {target_dt}: {e_hour}")
                continue
        
        logger.info(f"[FORECAST-JOB] ✓ Complete: {predictions_made} predictions generated")
        
        return {
            "status": "ok",
            "predictions_made": predictions_made,
            "target_date": now.date().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[FORECAST-JOB] Daily predictions failed: {e}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()




def run_hourly_reconciliation(target_date=None):
    """
    Hourly job - runs every hour (e.g., at :05)
    
    Re-reconciles ALL past hours of TODAY to catch late-arriving sales.
    Hours from previous days are left unchanged (finalized).
    Updates forecast_logs with valor_real and erro_percentual.

    Args:
        target_date: Optional. If string ('YYYY-MM-DD') or date object, specific date to reconcile.
                    If provided, bypasses the "only past hours of today" logic and processes ALL hours for that date
                    where we have data.
    """
    logger.info(f"[FORECAST-JOB] Starting hourly reconciliation (Target: {target_date})...")
    
    db = SessionLocal()
    
    try:
        from datetime import timezone
        tz_br = timezone(timedelta(hours=-3))
        
        now = datetime.now()
        now_local = now.replace(tzinfo=tz_br)
        
        # Determine logs to process
        if target_date:
            # Reconcile specific date
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            # Target start/end of that date
            day_start = datetime.combine(target_date, datetime.min.time())
            day_end = datetime.combine(target_date, datetime.max.time())
            
            # When forcing a date, we check ALL logs for that date
            # We must respect physics though - can't reconcile future if it hasn't happened.
            # But if the user forces "Today" at 16:00, we should reconcile 00:00-15:00.
            # If they force "Yesterday", we reconcile 00:00-23:00.
            
            logs_to_process = db.query(ForecastLog).filter(
                and_(
                    ForecastLog.hora_alvo >= day_start,
                    ForecastLog.hora_alvo <= day_end,
                    # We can only reconcile hours that have passed (hora_alvo < now)
                    # Unless we want to force 0 for future? No, that messes up stats.
                    ForecastLog.hora_alvo < now
                )
            ).all()
            
        else:
            # Standard logic (last 30 days pending, fully closed hours)
            cutoff_date = now - timedelta(days=30)
            
            logs_to_process = db.query(ForecastLog).filter(
                and_(
                    ForecastLog.hora_alvo >= cutoff_date,
                    ForecastLog.hora_alvo < now - timedelta(hours=1),  # Hour must be fully closed
                    # ForecastLog.valor_real.is_(None)  # REMOVED: Force re-check of all past hours to fix corrupted 0.00
                )
            ).all()
        
        if not logs_to_process:
            logger.info("[FORECAST-JOB] No pending logs to reconcile")
            return {"status": "ok", "reconciled": 0, "updated": 0}
        
        logger.info(f"[FORECAST-JOB] Reconciling {len(logs_to_process)} pending hours from last 30 days")
        
        reconciled_count = 0
        updated_count = 0
        
        for log in logs_to_process:
            hour_start = log.hora_alvo
            hour_end = hour_start + timedelta(hours=1)
            
            # Convert local time (Brasilia UTC-3) to UTC for database query
            hour_start_local = hour_start.replace(tzinfo=tz_br)
            hour_end_local = hour_end.replace(tzinfo=tz_br)
            
            hour_start_utc = hour_start_local.astimezone(timezone.utc).replace(tzinfo=None)
            hour_end_utc = hour_end_local.astimezone(timezone.utc).replace(tzinfo=None)

            actual_revenue = db.query(func.sum(MlOrder.total_amount)).filter(
                and_(
                    MlOrder.date_closed >= hour_start_utc,
                    MlOrder.date_closed < hour_end_utc,
                    MlOrder.status.in_(['paid', 'shipped', 'delivered'])
                )
            ).scalar()
            
            actual_revenue = float(actual_revenue or 0)
            
            logger.info(f"[DEBUG-RECONCILE] Processing {log.hora_alvo} | UTC Query: {hour_start_utc} to {hour_end_utc} | Revenue Found: {actual_revenue}")
            predicted = float(log.valor_previsto or 0)
            old_real = float(log.valor_real or 0)
            
            # Calculate error percentage
            if actual_revenue > 0:
                erro = ((predicted - actual_revenue) / actual_revenue) * 100
            else:
                erro = 0 if predicted == 0 else 100
            
            # Check if value changed (late sale arrived) or was previously empty
            was_empty = old_real == 0 and log.valor_real is None
            was_updated = not was_empty and abs(actual_revenue - old_real) > 0.01
            
            # DEEP RECONCILIATION: Update Product Mix with Real Sales
            # ---------------------------------------------------------
            if log.fatores_usados and '_product_mix' in log.fatores_usados:
                try:
                    # Query sold items details grouped by ID
                    sold_items = db.query(
                        MlOrderItem.ml_item_id,
                        func.sum(MlOrderItem.quantity).label('qty'),
                        func.sum(MlOrderItem.unit_price * MlOrderItem.quantity).label('rev')
                    ).join(MlOrder).filter(
                        and_(
                            MlOrder.date_closed >= hour_start_utc,
                            MlOrder.date_closed < hour_end_utc,
                            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
                        )
                    ).group_by(MlOrderItem.ml_item_id).all()
                    
                    # Create map
                    sold_map = {item.ml_item_id: {'qty': int(item.qty), 'rev': float(item.rev)} for item in sold_items}
                    
                    # Update mix
                    # Make a deep copy to ensure sqlalchemy tracks change
                    factors_copy = dict(log.fatores_usados)
                    mix = factors_copy['_product_mix']
                    
                    updated = False
                    for p in mix:
                        # Try matching by mlb_id (standard) or id
                        pid = p.get('mlb_id') or p.get('product_id') or p.get('id')
                        
                        if pid and pid in sold_map:
                            p['realized_units'] = sold_map[pid]['qty']
                            p['realized_revenue'] = sold_map[pid]['rev']
                            updated = True
                        else:
                            # Explicitly set to 0 if no match (to clear previous syncs/nulls)
                            if 'realized_units' not in p or p['realized_units'] != 0:
                                p['realized_units'] = 0
                                p['realized_revenue'] = 0.0
                                updated = True
                    
                    if updated:
                        log.fatores_usados = factors_copy
                        
                except Exception as deep_err:
                    logger.warning(f"[FORECAST-JOB] Deep reconciliation failed for log {log.id}: {deep_err}")

            # Update the log
            log.valor_real = Decimal(str(round(actual_revenue, 2)))
            log.erro_percentual = Decimal(str(round(erro, 2)))
            
            reconciled_count += 1
            if was_updated:
                updated_count += 1
                logger.debug(f"[FORECAST-JOB] Updated {log.hora_alvo}: R${old_real:.2f} -> R${actual_revenue:.2f}")
        
        db.commit()
        logger.info(f"[FORECAST-JOB] Reconciliation complete: {reconciled_count} new, {updated_count} updated")
        
        # Log to SystemLog for History UI
        try:
             # Calculate average error for the summary
             total_abs_error = 0
             count = 0
             for log in logs_to_process:  # Fixed: correct variable name
                 if log.valor_real is not None: # only reconciled ones
                    total_abs_error += abs(float(log.erro_percentual or 0))
                    count += 1
             
             avg_abs_error = total_abs_error / count if count > 0 else 0
             
             sys_log = SystemLog(
                 module='hyper_ai',
                 level='INFO',
                 message=f'Conciliação: {reconciled_count} previsões processadas',
                 details=json.dumps({
                     "action": "reconciliation",
                     "count": reconciled_count,
                     "avg_abs_error": round(avg_abs_error, 2),
                     "period": "hourly"
                 }),
                 duration_ms=0, # Optional
                 status='success'
             )
             db.add(sys_log)
             db.commit()
        except Exception as e_log:
            logger.error(f"Failed to write system log: {e_log}")

        return {
            "status": "ok", 
            "reconciled": reconciled_count
        }
        
    except Exception as e:
        logger.error(f"[FORECAST-JOB] Reconciliation failed: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


def run_weekly_calibration(force_run=False, target_date=None):
    """
    Hourly micro-calibration job (renamed from weekly for historical reasons).
    
    Analyzes error patterns from the past 24 hours (or specific target date).
    Makes small adjustments (max 1% per cycle) for faster learning.
    Minimum 3 samples required per factor.
    
    Args:
        force_run: If True, bypasses sample size limits and forces calibration.
                   Also allows re-calibrating logs that were already marked calibrated.
        target_date: Optional. Specific date to calibrate (overrides 'uncalibrated only' logic if forced).
    """
    logger.info(f"[FORECAST-JOB] Starting hourly micro-calibration (Force: {force_run}, Date: {target_date})...")
    
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(ForecastLog).filter(
            and_(
                ForecastLog.valor_real.isnot(None),
                ForecastLog.erro_percentual.isnot(None)
            )
        )
        
        # DATE FILTERING
        if target_date:
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            day_start = datetime.combine(target_date, datetime.min.time())
            day_end = datetime.combine(target_date, datetime.max.time())
            
            query = query.filter(
                and_(
                    ForecastLog.hora_alvo >= day_start,
                    ForecastLog.hora_alvo <= day_end
                )
            )
        
        # CALIBRATED STATUS FILTERING
        # If NOT forcing, only process uncalibrated ones
        # If forcing, we process EVERYTHING matching the date (re-calibration)
        if not force_run:
            query = query.filter(ForecastLog.calibrated != 'Y')
            
        logs = query.all()
        
        if len(logs) < 3 and not force_run:  # Minimum 3 samples for micro-calibration (unless forced)
            logger.info(f"[FORECAST-JOB] Not enough samples for calibration ({len(logs)} < 3)")
            return {"status": "skipped", "reason": "insufficient_samples", "samples": len(logs)}
        
        logger.info(f"[FORECAST-JOB] Analyzing {len(logs)} predictions from last 24h...")
        
        # Group errors by factor type
        factor_errors = _analyze_errors_by_factor(logs, force_run=force_run)
        
        # Apply micro-calibration adjustments
        adjustments_made = []
        
        for factor_type, factor_data in factor_errors.items():
            for factor_key, stats in factor_data.items():
                avg_error = stats["avg_error"]
                sample_count = stats["count"]
                
                # Minimum 3 samples for this specific factor (unless forced)
                if sample_count < 3 and not force_run:
                    continue
                
                
                # Check if error exceeds threshold (percent)
                # Standard: > 5% for micro-adjustments
                # Forced: > 0.1% (calibration on demand)
                threshold = 0.1 if force_run else 5.0
                
                if abs(avg_error) > threshold:
                    adjustment = _apply_micro_calibration(
                        db, factor_type, factor_key, avg_error, sample_count
                    )
                    if adjustment:
                        adjustments_made.append(adjustment)
        
        # Mark all logs used in this calibration as calibrated
        if adjustments_made:
            try:
                for log in logs:
                    if hasattr(log, 'calibrated'):
                        log.calibrated = 'Y'
                    # Store calibration impact for this log
                    if hasattr(log, 'calibration_impact') and not log.calibration_impact:
                        log.calibration_impact = adjustments_made
            except Exception as col_err:
                logger.warning(f"[FORECAST-JOB] Could not mark logs as calibrated: {col_err}")
        
        db.commit()
        
        logger.info(f"[FORECAST-JOB] Micro-calibration complete: {len(adjustments_made)} adjustments")
        
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


def _analyze_errors_by_factor(logs: List[ForecastLog], force_run: bool = False) -> Dict:
    """
    Group prediction errors by factor type to identify patterns.
    CRITICAL: Only uses categorical metadata keys (_meta_*), never numeric values.
    """
    factor_errors = {
        "day_of_week": {},
        "momentum": {},
        "period_of_month": {},
        "event": {},
        "seasonal": {},
        "hourly_pattern": {},
        "mobile_hours": {},
        "impulse_hours": {},
        "week_of_month": {},
        "payment_day": {}
    }

    # DYNAMIC WHITELIST (Database-driven)
    # Fetch allowed keys from database
    db = SessionLocal()
    allowed_factors_db = db.query(AllowedFactor).filter(AllowedFactor.is_active == 'Y').all()
    db.close()
    
    # Build dictionary for fast lookup: {'momentum': {'up', 'down'}, 'day_of_week': {...}}
    ALLOWED_KEYS = {}
    for af in allowed_factors_db:
        if af.factor_type not in ALLOWED_KEYS:
            ALLOWED_KEYS[af.factor_type] = set()
        ALLOWED_KEYS[af.factor_type].add(af.factor_key)
    
    # Add hardcoded fallback ONLY if DB is empty (safety net)
    if not ALLOWED_KEYS:
        ALLOWED_KEYS = {
            "day_of_week": {"segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"},
            "momentum": {"up", "down", "neutral", "normal", "default"},
            "period_of_month": {"inicio", "meio", "fim"},
            "seasonal": {"verao", "inverno", "outono", "primavera", "neutro"},
            "payment_day": {"quinto_dia_util", "dia_15", "dia_20", "normal"},
            "week_of_month": {"1", "2", "3", "4", "5"},
        }
        
    for log in logs:
        fatores = log.fatores_usados or {}
        erro = float(log.erro_percentual or 0)
        
        for factor_type in list(factor_errors.keys()):
            # ONLY use metadata key (categorical), NEVER the value
            meta_key = f"_meta_{factor_type}"
            
            if meta_key not in fatores:
                # Skip this factor if no categorical metadata exists
                continue
            
            categorical_key = str(fatores[meta_key])
            
            # 1. STRICT WHITELIST CHECK (The Guarantee)
            # Check if this TYPE is controlled by whitelist
            # If FORCE RUN, we relax this to allow learning everything
            if not force_run and factor_type in ALLOWED_KEYS:
                # Check if specific KEY is allowed
                if categorical_key not in ALLOWED_KEYS[factor_type]:
                    # REJECT: Key not in allowed list for this type
                    continue
            
            # 2. GENERAL SAFETY CHECK (For open types like 'event')
            if len(categorical_key) > 30 or ' ' in categorical_key:
                continue
            
            # Initialize if needed
            if categorical_key not in factor_errors[factor_type]:
                factor_errors[factor_type][categorical_key] = {"errors": [], "count": 0}
            
            # Add error
            factor_errors[factor_type][categorical_key]["errors"].append(erro)
            factor_errors[factor_type][categorical_key]["count"] += 1
    
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
    
    # Log to SystemLog for History UI
    try:
        sys_log = SystemLog(
             module='hyper_ai',
             level='INFO',
             message=f'Calibração: {factor_type}.{factor_key}',
             details=json.dumps({
                 "action": "calibration",
                 "factor": f"{factor_type}.{factor_key}",
                 "old_value": float(round(old_value, 3)),
                 "new_value": float(round(new_value, 3)),
                 "change_percent": float(round((new_value / old_value - 1) * 100, 2)),
                 "avg_error": float(round(avg_error, 2)),
                 "samples": sample_count
             }),
             status='success'
        )
        db.add(sys_log)
    except Exception as e_log:
        logger.error(f"Failed to write system log: {e_log}")
    
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


def _apply_micro_calibration(
    db: Session,
    factor_type: str,
    factor_key: str,
    avg_error: float,
    sample_count: int
) -> Dict:
    """
    Apply a MICRO calibration adjustment (max 1% per cycle) for faster learning.
    Respects the 'locked' flag - skips calibration if factor is locked.
    """
    # Get current multiplier value from config (or default to 1.0)
    config = db.query(MultiplierConfig).filter(
        and_(
            MultiplierConfig.tipo == factor_type,
            MultiplierConfig.chave == factor_key
        )
    ).first()
    
    # Check if locked - skip calibration if locked
    if config and getattr(config, 'locked', 'N') == 'Y':
        logger.debug(f"[FORECAST-JOB] Skipping locked factor: {factor_type}.{factor_key}")
        return None
    
    old_value = float(config.valor) if config else 1.0
    
    # Micro-adjustment: max 1% per cycle (vs 2% for weekly)
    adjustment_factor = 0.01
    
    if avg_error > 5:
        new_value = old_value * (1 - adjustment_factor)
    elif avg_error < -5:
        new_value = old_value * (1 + adjustment_factor)
    else:
        return None
    
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
        notas=f"Micro-calibration (hourly): avg_error={avg_error:.1f}% samples={sample_count}"
    )
    db.add(history)
    
    logger.info(f"[FORECAST-JOB] Micro-calibrated {factor_type}.{factor_key}: {old_value:.3f} -> {new_value:.3f} (±1%)")
    
    return {
        "factor_type": factor_type,
        "factor_key": factor_key,
        "old_value": old_value,
        "new_value": round(new_value, 3),
        "avg_error": round(avg_error, 1),
        "samples": sample_count
    }


def run_daily_snapshot():
    """
    Daily job - runs at 23:55
    
    Creates a snapshot of the day's learning metrics for historical analysis.
    """
    from app.models.forecast_learning import LearningSnapshot
    
    logger.info("[FORECAST-JOB] Creating daily learning snapshot...")
    
    db = SessionLocal()
    
    try:
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Get today's reconciled logs
        logs = db.query(ForecastLog).filter(
            and_(
                ForecastLog.hora_alvo >= today_start,
                ForecastLog.hora_alvo <= today_end,
                ForecastLog.valor_real.isnot(None)
            )
        ).all()
        
        if not logs:
            logger.info("[FORECAST-JOB] No logs to snapshot for today")
            return {"status": "skipped", "reason": "no_data"}
        
        # Calculate metrics
        total_previsto = sum(float(l.valor_previsto or 0) for l in logs)
        total_real = sum(float(l.valor_real or 0) for l in logs)
        errors = [float(l.erro_percentual or 0) for l in logs if l.erro_percentual is not None]
        
        erro_medio = sum(errors) / len(errors) if errors else 0
        erro_abs_medio = sum(abs(e) for e in errors) / len(errors) if errors else 0
        acuracia = max(0, 100 - erro_abs_medio)
        
        # Calculate factor performance
        fatores_performance = {}
        for log in logs:
            if log.fatores_usados:
                erro = float(log.erro_percentual or 0)
                for factor_type, factor_value in log.fatores_usados.items():
                    if factor_type not in fatores_performance:
                        fatores_performance[factor_type] = {}
                    key = str(factor_value)
                    if key not in fatores_performance[factor_type]:
                        fatores_performance[factor_type][key] = {"errors": [], "count": 0}
                    fatores_performance[factor_type][key]["errors"].append(erro)
                    fatores_performance[factor_type][key]["count"] += 1
        
        # Average errors per factor
        for ft in fatores_performance:
            for key in fatores_performance[ft]:
                errs = fatores_performance[ft][key]["errors"]
                fatores_performance[ft][key] = round(sum(errs) / len(errs), 2) if errs else 0
        
        # Find best/worst factors
        all_factor_errors = []
        for ft, keys in fatores_performance.items():
            for key, err in keys.items():
                all_factor_errors.append((f"{ft}.{key}", abs(err)))
        
        melhor_fator = min(all_factor_errors, key=lambda x: x[1])[0] if all_factor_errors else None
        pior_fator = max(all_factor_errors, key=lambda x: x[1])[0] if all_factor_errors else None
        
        # Get today's calibrations
        calibracoes = db.query(CalibrationHistory).filter(
            CalibrationHistory.data_calibracao >= today_start
        ).all()
        
        detalhes_ajustes = [
            {
                "factor": f"{c.tipo_fator}.{c.fator_chave}",
                "change": f"{c.valor_anterior} -> {c.valor_novo}",
                "error": float(c.erro_medio)
            } for c in calibracoes
        ]
        
        # Create or update snapshot
        snapshot = db.query(LearningSnapshot).filter(LearningSnapshot.data == today).first()
        if not snapshot:
            snapshot = LearningSnapshot(data=today)
            db.add(snapshot)
        
        snapshot.total_previsoes = len(logs)
        snapshot.erro_medio = Decimal(str(round(erro_medio, 2)))
        snapshot.erro_absoluto_medio = Decimal(str(round(erro_abs_medio, 2)))
        snapshot.acuracia = Decimal(str(round(acuracia, 2)))
        snapshot.receita_prevista_total = Decimal(str(round(total_previsto, 2)))
        snapshot.receita_real_total = Decimal(str(round(total_real, 2)))
        snapshot.fatores_performance = fatores_performance
        snapshot.ajustes_realizados = len(calibracoes)
        snapshot.detalhes_ajustes = detalhes_ajustes
        snapshot.melhor_fator = melhor_fator
        snapshot.pior_fator = pior_fator
        
        db.commit()
        
        logger.info(f"[FORECAST-JOB] Daily snapshot created: {today} - accuracy={acuracia:.1f}%")
        
        return {
            "status": "ok",
            "date": today.isoformat(),
            "accuracy": round(acuracia, 2),
            "predictions": len(logs),
            "calibrations": len(calibracoes)
        }
        
    except Exception as e:
        logger.error(f"[FORECAST-JOB] Daily snapshot failed: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()
