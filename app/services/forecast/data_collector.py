"""
Hyper Forecast - Data Collector Module
Collects and aggregates historical sales data by hour for forecasting
"""
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.ml_order import MlOrder, MlOrderItem

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Collects historical sales data aggregated by hour for forecasting
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_hourly_sales(
        self, 
        target_date: date, 
        target_hour: int
    ) -> Dict:
        """
        Get sales data for a specific date and hour
        """
        start_dt = datetime.combine(target_date, datetime.min.time()).replace(hour=target_hour)
        end_dt = start_dt + timedelta(hours=1)
        
        result = self.db.query(
            func.count(MlOrder.id).label('order_count'),
            func.sum(MlOrder.total_amount).label('revenue')
        ).filter(
            and_(
                MlOrder.date_closed >= start_dt,
                MlOrder.date_closed < end_dt,
                MlOrder.status.in_(['paid', 'shipped', 'delivered'])
            )
        ).first()
        
        return {
            "date": target_date,
            "hour": target_hour,
            "order_count": result.order_count or 0,
            "revenue": float(result.revenue or 0)
        }
    
    def get_hourly_pattern(
        self, 
        days_back: int = 30
    ) -> Dict[int, Dict]:
        """
        Calculate average sales pattern by hour over the last N days
        Returns dict with hour (0-23) as key
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Query hourly aggregates
        results = self.db.query(
            func.extract('hour', MlOrder.date_closed).label('hour'),
            func.count(MlOrder.id).label('order_count'),
            func.sum(MlOrder.total_amount).label('revenue')
        ).filter(
            and_(
                MlOrder.date_closed >= start_date,
                MlOrder.date_closed <= end_date,
                MlOrder.status.in_(['paid', 'shipped', 'delivered'])
            )
        ).group_by(
            func.extract('hour', MlOrder.date_closed)
        ).all()
        
        # Calculate averages
        pattern = {}
        for row in results:
            hour = int(row.hour)
            pattern[hour] = {
                "avg_orders": (row.order_count or 0) / days_back,
                "avg_revenue": float(row.revenue or 0) / days_back,
                "total_orders": row.order_count or 0,
                "total_revenue": float(row.revenue or 0)
            }
        
        # Fill missing hours with zeros
        for h in range(24):
            if h not in pattern:
                pattern[h] = {
                    "avg_orders": 0,
                    "avg_revenue": 0,
                    "total_orders": 0,
                    "total_revenue": 0
                }
        
        return pattern
    
    def get_day_of_week_pattern(
        self, 
        days_back: int = 90
    ) -> Dict[int, float]:
        """
        Calculate relative sales multiplier by day of week
        0=Monday, 6=Sunday
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        results = self.db.query(
            func.extract('dow', MlOrder.date_closed).label('dow'),
            func.sum(MlOrder.total_amount).label('revenue')
        ).filter(
            and_(
                MlOrder.date_closed >= start_date,
                MlOrder.date_closed <= end_date,
                MlOrder.status.in_(['paid', 'shipped', 'delivered'])
            )
        ).group_by(
            func.extract('dow', MlOrder.date_closed)
        ).all()
        
        # Calculate average across all days
        total_revenue = sum(r.revenue or 0 for r in results)
        avg_per_day = total_revenue / 7 if total_revenue > 0 else 1
        
        # Calculate multipliers relative to average
        pattern = {}
        for row in results:
            dow = int(row.dow)  # PostgreSQL: 0=Sunday, 1=Monday...
            # Convert to Python: 0=Monday, 6=Sunday
            python_dow = (dow - 1) % 7 if dow > 0 else 6
            revenue = float(row.revenue or 0)
            pattern[python_dow] = revenue / avg_per_day if avg_per_day > 0 else 1.0
        
        # Fill missing days
        for d in range(7):
            if d not in pattern:
                pattern[d] = 1.0
        
        return pattern
    
    def get_sales_same_hour_history(
        self,
        target_hour: int,
        days_back_list: List[int] = [1, 7, 14, 30]
    ) -> Dict[str, Optional[float]]:
        """
        Get sales for the same hour on specific days back
        Used for weighted baseline calculation
        """
        today = datetime.now().date()
        history = {}
        
        for days_back in days_back_list:
            target_date = today - timedelta(days=days_back)
            data = self.get_hourly_sales(target_date, target_hour)
            history[f"days_{days_back}"] = data["revenue"]
        
        return history
    
    def get_sales_today_so_far(self) -> List[Dict]:
        """
        Get hourly sales for today up to current hour
        """
        today = datetime.now().date()
        current_hour = datetime.now().hour
        
        hourly_data = []
        for hour in range(current_hour + 1):
            data = self.get_hourly_sales(today, hour)
            hourly_data.append(data)
        
        return hourly_data
    
    def get_sales_previous_period(
        self,
        reference_date: date,
        compare_type: str = "week"  # "day", "week", "month"
    ) -> List[Dict]:
        """
        Get full day sales for a comparison period
        """
        if compare_type == "day":
            target_date = reference_date - timedelta(days=1)
        elif compare_type == "week":
            target_date = reference_date - timedelta(days=7)
        elif compare_type == "month":
            target_date = reference_date - timedelta(days=30)
        else:
            target_date = reference_date - timedelta(days=7)
        
        hourly_data = []
        for hour in range(24):
            data = self.get_hourly_sales(target_date, hour)
            hourly_data.append(data)
        
        return hourly_data
