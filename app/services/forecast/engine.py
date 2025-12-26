"""
Hyper Forecast - Main Engine
Combines all multipliers to generate sales predictions
"""
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .data_collector import DataCollector
from .baseline import BaselineCalculator
from .multipliers.calendar import CalendarMultipliers
from .multipliers.momentum import MomentumCalculator

logger = logging.getLogger(__name__)


class HyperForecast:
    """
    Main forecasting engine that combines all prediction factors
    
    Formula: PREDICTION = BASELINE × Π(MULTIPLIERS) × MOMENTUM_FACTOR
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.data_collector = DataCollector(db)
        self.baseline_calc = BaselineCalculator(db)
        self.calendar_mult = CalendarMultipliers()
        self.momentum_calc = MomentumCalculator(db)
    
    def predict_hour(
        self,
        target_hour: int,
        target_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Generate prediction for a specific hour
        
        Args:
            target_hour: Hour (0-23) to predict
            target_date: Date to predict (defaults to today)
            category: Optional product category for seasonal adjustments
        
        Returns:
            Dict with prediction, confidence, and factor breakdown
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        # 1. Calculate baseline from historical data
        baseline_result = self.baseline_calc.calculate_baseline(target_hour, target_date)
        baseline = baseline_result["baseline"]
        baseline_confidence = baseline_result["confidence"]
        
        # 2. Get calendar multipliers
        calendar = self.calendar_mult.get_all_calendar_multipliers(target_date, category)
        
        # 3. Get momentum (only if predicting future hours today)
        now = datetime.now()
        is_future = target_date >= now.date() and target_hour > now.hour
        
        if is_future and target_date == now.date():
            momentum_result = self.momentum_calc.calculate_momentum()
            momentum_mult = momentum_result["multiplier"]
            momentum_reason = momentum_result["reason"]
        else:
            momentum_mult = 1.0
            momentum_reason = "N/A (hora passada)"
        
        # 4. Combine all multipliers
        all_multipliers = {
            "day_of_week": calendar["day_of_week"],
            "period_of_month": calendar["period_of_month"],
            "event": calendar["event"],
            "seasonal": calendar["seasonal"],
            "momentum": momentum_mult,
        }
        
        combined_multiplier = 1.0
        for mult in all_multipliers.values():
            combined_multiplier *= mult
        
        # 5. Calculate prediction
        prediction = baseline * combined_multiplier
        
        # 6. Calculate confidence interval
        # Wider interval when more extreme multipliers are applied
        deviation_factor = sum(abs(m - 1.0) for m in all_multipliers.values())
        
        if deviation_factor < 0.3:
            confidence_range = 0.20  # ±20%
            confidence_level = 0.85
        elif deviation_factor < 0.6:
            confidence_range = 0.30  # ±30%
            confidence_level = 0.70
        elif deviation_factor < 1.0:
            confidence_range = 0.40  # ±40%
            confidence_level = 0.55
        else:
            confidence_range = 0.50  # ±50%
            confidence_level = 0.40
        
        # Adjust confidence by baseline confidence
        final_confidence = confidence_level * baseline_confidence
        
        min_prediction = prediction * (1 - confidence_range)
        max_prediction = prediction * (1 + confidence_range)
        
        return {
            "hour": target_hour,
            "hour_label": f"{target_hour:02d}h",
            "date": target_date.isoformat(),
            "prediction": round(prediction, 2),
            "min": round(min_prediction, 2),
            "max": round(max_prediction, 2),
            "confidence": round(final_confidence, 2),
            "baseline": round(baseline, 2),
            "combined_multiplier": round(combined_multiplier, 3),
            "multipliers": all_multipliers,
            "factors": {
                "event_name": calendar.get("event_name"),
                "season_name": calendar.get("season_name"),
                "momentum_reason": momentum_reason,
            },
            "is_future": is_future,
        }
    
    def _log_prediction(
        self,
        target_date: date,
        target_hour: int,
        prediction: float,
        baseline: float,
        multipliers: Dict
    ) -> int:
        """
        Log prediction to forecast_logs table for future learning
        
        Returns:
            ID of the created log entry
        """
        try:
            from app.models.forecast_learning import ForecastLog
            
            hora_alvo = datetime.combine(target_date, datetime.min.time()).replace(hour=target_hour)
            
            log_entry = ForecastLog(
                timestamp_previsao=datetime.utcnow(),
                hora_alvo=hora_alvo,
                valor_previsto=prediction,
                fatores_usados=multipliers,
                baseline_usado=baseline,
                modelo_versao='heuristic_v1'
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
            logger.debug(f"[FORECAST] Logged prediction for {hora_alvo}: R${prediction:.2f}")
            return log_entry.id
            
        except Exception as e:
            logger.warning(f"[FORECAST] Failed to log prediction: {e}")
            self.db.rollback()
            return -1
    
    def predict_hour_with_logging(
        self,
        target_hour: int,
        target_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Generate prediction AND log it for learning system
        Use this method when you want predictions to be tracked
        """
        result = self.predict_hour(target_hour, target_date, category)
        
        # Only log future predictions (past predictions are useless for learning)
        if result["is_future"]:
            log_id = self._log_prediction(
                target_date=target_date or datetime.now().date(),
                target_hour=target_hour,
                prediction=result["prediction"],
                baseline=result["baseline"],
                multipliers=result["multipliers"]
            )
            result["log_id"] = log_id
        
        return result
    
    def predict_day(
        self,
        target_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Generate predictions for an entire day (all 24 hours)
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        hourly_predictions = []
        total_predicted = 0
        total_min = 0
        total_max = 0
        avg_confidence = 0
        
        for hour in range(24):
            pred = self.predict_hour(hour, target_date, category)
            hourly_predictions.append(pred)
            total_predicted += pred["prediction"]
            total_min += pred["min"]
            total_max += pred["max"]
            avg_confidence += pred["confidence"]
        
        # Find peak and valley hours
        peak = max(hourly_predictions, key=lambda x: x["prediction"])
        valley = min(hourly_predictions, key=lambda x: x["prediction"])
        
        return {
            "date": target_date.isoformat(),
            "total_predicted": round(total_predicted, 2),
            "total_min": round(total_min, 2),
            "total_max": round(total_max, 2),
            "avg_confidence": round(avg_confidence / 24, 2),
            "hourly": hourly_predictions,
            "peak_hour": {
                "hour": peak["hour_label"],
                "prediction": peak["prediction"]
            },
            "valley_hour": {
                "hour": valley["hour_label"],
                "prediction": valley["prediction"]
            }
        }
    
    def get_today_with_actuals(self) -> Dict:
        """
        Get today's forecast combined with actual sales data
        Perfect for the dashboard chart
        """
        today = datetime.now().date()
        current_hour = datetime.now().hour
        
        # Get predictions for all 24 hours
        day_forecast = self.predict_day(today)
        
        # Get actual sales up to current hour
        actuals = self.data_collector.get_sales_today_so_far()
        actual_total = sum(h["revenue"] for h in actuals)
        
        # Get previous period for comparison
        previous = self.data_collector.get_sales_previous_period(today, "week")
        previous_total = sum(h["revenue"] for h in previous)
        
        # Calculate remaining prediction (future hours only)
        remaining_predicted = sum(
            p["prediction"] 
            for p in day_forecast["hourly"] 
            if p["hour"] > current_hour
        )
        
        # Project end of day
        projected_total = actual_total + remaining_predicted
        
        # Comparison with previous period
        vs_previous_percent = ((projected_total - previous_total) / previous_total * 100) if previous_total > 0 else 0
        
        return {
            "date": today.isoformat(),
            "current_hour": current_hour,
            "actual_total": round(actual_total, 2),
            "remaining_predicted": round(remaining_predicted, 2),
            "projected_total": round(projected_total, 2),
            "projected_min": round(actual_total + sum(p["min"] for p in day_forecast["hourly"] if p["hour"] > current_hour), 2),
            "projected_max": round(actual_total + sum(p["max"] for p in day_forecast["hourly"] if p["hour"] > current_hour), 2),
            "previous_period_total": round(previous_total, 2),
            "vs_previous_percent": round(vs_previous_percent, 1),
            "avg_confidence": day_forecast["avg_confidence"],
            "hourly": {
                "actuals": actuals,
                "predictions": day_forecast["hourly"],
                "previous": previous
            },
            "peak_hour": day_forecast["peak_hour"],
            "valley_hour": day_forecast["valley_hour"]
        }
