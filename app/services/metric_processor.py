
import logging
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ad import Ad
from app.models.ml_metrics_daily import MlMetricsDaily

logger = logging.getLogger(__name__)

class MetricProcessor:
    def __init__(self, db_session: Session):
        self.db = db_session

    def process_trends(self, ad_id: str):
        """
        Calculates 7-day trends for Visits and Sales.
        Formula: ((Current 7d Avg - Previous 7d Avg) / Previous 7d Avg) * 100
        Or simple sum comparison: ((Sum 7d Current - Sum 7d Previous) / Sum 7d Previous) * 100
        """
        try:
            today = datetime.date.today()
            # 7 Days Current: [Today-7, Today-1] (Last completed 7 days usually better)
            # Let's use last 7 days including today? Or excluding today (incomplete)? 
            # Excluding today is safer for "completed" metrics.
            
            end_date = today - datetime.timedelta(days=1)
            start_date_current = end_date - datetime.timedelta(days=6) # 7 days window
            
            end_date_prev = start_date_current - datetime.timedelta(days=1)
            start_date_prev = end_date_prev - datetime.timedelta(days=6) # 7 days window

            # Query Metrics
            # We need sum of visits and sales for these periods
            
            # Current Window
            current_metrics = self.db.query(
                func.sum(MlMetricsDaily.visits),
                func.sum(MlMetricsDaily.sales_qty)
            ).filter(
                MlMetricsDaily.item_id == ad_id,
                MlMetricsDaily.date >= start_date_current,
                MlMetricsDaily.date <= end_date
            ).first()
            
            # Previous Window
            prev_metrics = self.db.query(
                func.sum(MlMetricsDaily.visits),
                func.sum(MlMetricsDaily.sales_qty)
            ).filter(
                MlMetricsDaily.item_id == ad_id,
                MlMetricsDaily.date >= start_date_prev,
                MlMetricsDaily.date <= end_date_prev
            ).first()
            
            curr_visits = current_metrics[0] or 0
            curr_sales = current_metrics[1] or 0
            prev_visits = prev_metrics[0] or 0
            prev_sales = prev_metrics[1] or 0
            
            # Calc Changes
            visits_change = 0.0
            if prev_visits > 0:
                visits_change = ((curr_visits - prev_visits) / prev_visits) * 100
            elif curr_visits > 0:
                visits_change = 100.0 # New traffic
                
            sales_change = 0.0
            if prev_sales > 0:
                sales_change = ((curr_sales - prev_sales) / prev_sales) * 100
            elif curr_sales > 0:
                sales_change = 100.0
                
            return visits_change, sales_change
            
        except Exception as e:
            logger.error(f"Error calculating trends for {ad_id}: {e}")
            return None, None

    def calculate_days_of_stock(self, ad: Ad):
        """
        Calculates estimated days of stock based on 30d sales.
        Formula: Available Quantity / (Sales 30d / 30)
        """
        try:
            if not ad.sales_30d or ad.sales_30d <= 0:
                return 999.0 # Infinite/High stock relative to 0 sales
            
            daily_sales_avg = ad.sales_30d / 30.0
            if daily_sales_avg == 0:
                return 999.0
                
            days = ad.available_quantity / daily_sales_avg
            return round(days, 1)
        except Exception as e:
            logger.error(f"Error calculating DOS for {ad.id}: {e}")
            return 0.0

    def process_all(self):
        """
        Runs processing for all active ads.
        """
        ads = self.db.query(Ad).filter(Ad.status == 'active').all()
        count = 0
        for ad in ads:
            # 1. Trends
            v_change, s_change = self.process_trends(ad.id)
            if v_change is not None:
                ad.visits_7d_change = v_change
            if s_change is not None:
                ad.sales_7d_change = s_change
            
            # 2. Stock Analysis
            ad.days_of_stock = self.calculate_days_of_stock(ad)
            
            count += 1
        
        self.db.commit()
        logger.info(f"Processed metrics for {count} ads.")

    def aggregate_sales_metrics(self):
        """
        Aggregates sales from MlOrders into Ad.sales_30d.
        """
        logger.info("Aggregating Sales Metrics from Orders...")
        try:
            # Reset sales_30d for active ads first (optional, but safer to avoid stale data if no orders)
            # self.db.query(Ad).update({Ad.sales_30d: 0}) # Might be heavy?
            # Better: query aggregation first, then bulk update.
            
            today = datetime.date.today()
            start_date = today - datetime.timedelta(days=30)
            
            # Query: ItemID, Sum(Quantity)
            from app.models.ml_order import MlOrder, MlOrderItem
            
            results = self.db.query(
                MlOrderItem.ml_item_id,
                func.sum(MlOrderItem.quantity)
            ).join(MlOrder, MlOrder.ml_order_id == MlOrderItem.ml_order_id)\
             .filter(MlOrder.date_created >= start_date)\
             .group_by(MlOrderItem.ml_item_id)\
             .all()
             
            # Update Ads
            # We can iterate and update.
            count = 0
            for item_id, total_qty in results:
                if total_qty:
                    ad = self.db.query(Ad).filter(Ad.id == item_id).first()
                    if ad:
                        ad.sales_30d = int(total_qty)
                        count += 1
            
            self.db.commit()
            logger.info(f"Updated sales_30d for {count} ads.")
            
        except Exception as e:
            logger.error(f"Failed to aggregate sales metrics: {e}")
            self.db.rollback()
