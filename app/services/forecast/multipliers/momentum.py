"""
Hyper Forecast - Momentum Calculator
Calculates short-term trend adjustments based on recent performance vs expected
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..data_collector import DataCollector
from ..baseline import BaselineCalculator

logger = logging.getLogger(__name__)


class MomentumCalculator:
    """
    Calculates momentum multiplier based on recent sales vs expected
    If recent hours are performing above/below expectations, adjust future predictions
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.data_collector = DataCollector(db)
        self.baseline_calc = BaselineCalculator(db)
    
    def calculate_momentum(
        self,
        hours_lookback: int = 4,
        smoothing_factor: float = 0.5
    ) -> Dict:
        """
        Calculate momentum multiplier based on last N hours performance
        
        Args:
            hours_lookback: How many recent hours to analyze
            smoothing_factor: How much to dampen the adjustment (0.5 = half the deviation)
        
        Returns:
            Dict with momentum multiplier and analysis details
        """
        now = datetime.now()
        current_hour = now.hour
        today = now.date()
        
        # Need at least 1 hour of data
        if current_hour < 1:
            return {
                "multiplier": 1.0,
                "confidence": 0.3,
                "reason": "Dados insuficientes (início do dia)",
                "details": {}
            }
        
        # Analyze recent hours
        actual_total = 0
        expected_total = 0
        hours_analyzed = 0
        details = []
        
        for hour_offset in range(1, min(hours_lookback + 1, current_hour + 1)):
            hour = current_hour - hour_offset
            
            # Get actual sales
            actual = self.data_collector.get_hourly_sales(today, hour)
            actual_revenue = actual["revenue"]
            
            # Get expected (baseline)
            baseline = self.baseline_calc.calculate_baseline(hour, today)
            expected_revenue = baseline["baseline"]
            
            if expected_revenue > 0:
                actual_total += actual_revenue
                expected_total += expected_revenue
                hours_analyzed += 1
                
                details.append({
                    "hour": f"{hour:02d}h",
                    "actual": actual_revenue,
                    "expected": expected_revenue,
                    "ratio": actual_revenue / expected_revenue if expected_revenue > 0 else 1.0
                })
        
        if expected_total == 0 or hours_analyzed == 0:
            return {
                "multiplier": 1.0,
                "confidence": 0.3,
                "reason": "Sem baseline histórico para comparação",
                "details": details
            }
        
        # Calculate raw momentum ratio
        raw_ratio = actual_total / expected_total
        
        # Apply smoothing (don't over-react to short-term variations)
        # If ratio is 1.2 (20% above), with 0.5 smoothing, multiplier becomes 1.1
        deviation = raw_ratio - 1.0
        smoothed_deviation = deviation * smoothing_factor
        multiplier = 1.0 + smoothed_deviation
        
        # Limit the range to prevent extreme adjustments
        multiplier = max(0.70, min(1.40, multiplier))
        
        # Determine reason/direction
        if multiplier > 1.05:
            reason = f"Vendas {((raw_ratio - 1) * 100):.1f}% acima do esperado nas últimas {hours_analyzed}h"
            direction = "up"
        elif multiplier < 0.95:
            reason = f"Vendas {((1 - raw_ratio) * 100):.1f}% abaixo do esperado nas últimas {hours_analyzed}h"
            direction = "down"
        else:
            reason = "Vendas dentro do esperado"
            direction = "neutral"
        
        # Confidence based on hours analyzed
        confidence = min(0.9, 0.4 + (hours_analyzed * 0.1))
        
        return {
            "multiplier": round(multiplier, 3),
            "raw_ratio": round(raw_ratio, 3),
            "actual_total": actual_total,
            "expected_total": expected_total,
            "hours_analyzed": hours_analyzed,
            "direction": direction,
            "confidence": confidence,
            "reason": reason,
            "details": details
        }
    
    def calculate_error_correction(
        self,
        days_lookback: int = 7
    ) -> Dict:
        """
        Calculate correction factor based on recent prediction errors
        If the model consistently over/under-predicts, apply a correction
        """
        # This would require storing historical predictions
        # For MVP, return neutral
        # TODO: Implement prediction history storage and error analysis
        
        return {
            "correction_factor": 1.0,
            "avg_error": 0.0,
            "reason": "Correção de erro não implementada ainda"
        }
