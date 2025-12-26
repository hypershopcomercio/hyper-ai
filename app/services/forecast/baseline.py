"""
Hyper Forecast - Baseline Calculator Module
Calculates weighted baseline predictions using temporal hierarchy
"""
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Optional
from sqlalchemy.orm import Session
from .data_collector import DataCollector

logger = logging.getLogger(__name__)


# Temporal weights for baseline calculation
TEMPORAL_WEIGHTS = {
    "same_hour_yesterday": 0.25,
    "same_hour_week_ago": 0.20,
    "same_hour_2weeks_ago": 0.15,
    "average_7d": 0.20,
    "average_30d": 0.10,
    "same_hour_month_ago": 0.10,
}

# Standard e-commerce hourly curve (relative to daily average)
# Calibrated for Brazilian market
DEFAULT_HOURLY_CURVE = {
    0: 0.45, 1: 0.25, 2: 0.15, 3: 0.10,
    4: 0.08, 5: 0.12, 6: 0.25, 7: 0.45,
    8: 0.70, 9: 0.95, 10: 1.15, 11: 1.25,
    12: 1.10, 13: 1.20, 14: 1.15, 15: 1.10,
    16: 1.05, 17: 1.00, 18: 1.10, 19: 1.35,
    20: 1.55, 21: 1.65, 22: 1.45, 23: 0.95,
}


class BaselineCalculator:
    """
    Calculates baseline sales predictions using weighted historical data
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.data_collector = DataCollector(db)
        self._hourly_curve_cache = None
        self._dow_pattern_cache = None
    
    def get_hourly_curve(self, force_refresh: bool = False) -> Dict[int, float]:
        """
        Get calibrated hourly sales curve based on actual data
        Falls back to default curve if not enough data
        """
        if self._hourly_curve_cache and not force_refresh:
            return self._hourly_curve_cache
        
        try:
            pattern = self.data_collector.get_hourly_pattern(days_back=30)
            
            # Calculate total and average
            total_revenue = sum(p["avg_revenue"] for p in pattern.values())
            if total_revenue == 0:
                logger.warning("No historical data, using default curve")
                return DEFAULT_HOURLY_CURVE
            
            avg_hourly = total_revenue / 24
            
            # Calculate relative curve
            curve = {}
            for hour in range(24):
                if hour in pattern and avg_hourly > 0:
                    curve[hour] = pattern[hour]["avg_revenue"] / avg_hourly
                else:
                    curve[hour] = DEFAULT_HOURLY_CURVE.get(hour, 1.0)
            
            self._hourly_curve_cache = curve
            return curve
            
        except Exception as e:
            logger.error(f"Error calculating hourly curve: {e}")
            return DEFAULT_HOURLY_CURVE
    
    def calculate_baseline(
        self,
        target_hour: int,
        target_date: Optional[date] = None
    ) -> Dict:
        """
        Calculate weighted baseline for a specific hour
        Uses temporal hierarchy with different weights for different historical periods
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        # Collect historical data points
        data_points = {}
        weights_used = {}
        
        # Yesterday same hour
        yesterday = target_date - timedelta(days=1)
        yday_data = self.data_collector.get_hourly_sales(yesterday, target_hour)
        if yday_data["revenue"] > 0:
            data_points["same_hour_yesterday"] = yday_data["revenue"]
            weights_used["same_hour_yesterday"] = TEMPORAL_WEIGHTS["same_hour_yesterday"]
        
        # Week ago same hour
        week_ago = target_date - timedelta(days=7)
        week_data = self.data_collector.get_hourly_sales(week_ago, target_hour)
        if week_data["revenue"] > 0:
            data_points["same_hour_week_ago"] = week_data["revenue"]
            weights_used["same_hour_week_ago"] = TEMPORAL_WEIGHTS["same_hour_week_ago"]
        
        # 2 weeks ago same hour
        two_weeks_ago = target_date - timedelta(days=14)
        tw_data = self.data_collector.get_hourly_sales(two_weeks_ago, target_hour)
        if tw_data["revenue"] > 0:
            data_points["same_hour_2weeks_ago"] = tw_data["revenue"]
            weights_used["same_hour_2weeks_ago"] = TEMPORAL_WEIGHTS["same_hour_2weeks_ago"]
        
        # Month ago same hour
        month_ago = target_date - timedelta(days=30)
        month_data = self.data_collector.get_hourly_sales(month_ago, target_hour)
        if month_data["revenue"] > 0:
            data_points["same_hour_month_ago"] = month_data["revenue"]
            weights_used["same_hour_month_ago"] = TEMPORAL_WEIGHTS["same_hour_month_ago"]
        
        # 7-day average for this hour
        pattern_7d = self.data_collector.get_hourly_pattern(days_back=7)
        if target_hour in pattern_7d and pattern_7d[target_hour]["avg_revenue"] > 0:
            data_points["average_7d"] = pattern_7d[target_hour]["avg_revenue"]
            weights_used["average_7d"] = TEMPORAL_WEIGHTS["average_7d"]
        
        # 30-day average for this hour
        pattern_30d = self.data_collector.get_hourly_pattern(days_back=30)
        if target_hour in pattern_30d and pattern_30d[target_hour]["avg_revenue"] > 0:
            data_points["average_30d"] = pattern_30d[target_hour]["avg_revenue"]
            weights_used["average_30d"] = TEMPORAL_WEIGHTS["average_30d"]
        
        # Calculate weighted baseline
        if not data_points:
            # Fallback: use hourly curve with estimated daily average
            curve = self.get_hourly_curve()
            estimated_daily = self._estimate_daily_average()
            baseline = estimated_daily * curve.get(target_hour, 1.0) / 24
            
            return {
                "baseline": baseline,
                "confidence": 0.3,
                "data_points": {},
                "method": "fallback_curve"
            }
        
        # Normalize weights
        total_weight = sum(weights_used.values())
        normalized_weights = {k: v / total_weight for k, v in weights_used.items()}
        
        # Calculate weighted average
        baseline = sum(
            data_points[key] * normalized_weights[key]
            for key in data_points
        )
        
        # Calculate confidence based on data availability
        confidence = min(1.0, len(data_points) / 6 * 0.9)
        
        return {
            "baseline": baseline,
            "confidence": confidence,
            "data_points": data_points,
            "weights": normalized_weights,
            "method": "weighted_average"
        }
    
    def calculate_day_baseline(
        self,
        target_date: Optional[date] = None
    ) -> Dict:
        """
        Calculate baseline for entire day (all 24 hours)
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        hourly_baselines = []
        total_baseline = 0
        avg_confidence = 0
        
        for hour in range(24):
            result = self.calculate_baseline(hour, target_date)
            hourly_baselines.append({
                "hour": hour,
                "baseline": result["baseline"],
                "confidence": result["confidence"]
            })
            total_baseline += result["baseline"]
            avg_confidence += result["confidence"]
        
        return {
            "date": target_date.isoformat(),
            "total_baseline": total_baseline,
            "avg_confidence": avg_confidence / 24,
            "hourly": hourly_baselines
        }
    
    def _estimate_daily_average(self) -> float:
        """
        Estimate average daily revenue from last 30 days
        """
        try:
            pattern = self.data_collector.get_hourly_pattern(days_back=30)
            total_hourly_avg = sum(p["avg_revenue"] for p in pattern.values())
            return total_hourly_avg
        except Exception:
            return 1000.0  # Fallback estimate
