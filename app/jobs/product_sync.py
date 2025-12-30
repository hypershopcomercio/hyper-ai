"""
Hyper Forecast V2 - Product Metrics Sync Job
Calculates and syncs product-level metrics for intelligent forecasting
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from decimal import Decimal
from typing import Dict, List

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.product_forecast import ProductForecast

logger = logging.getLogger(__name__)


def sync_product_metrics():
    """
    Main job to sync product-level metrics for forecasting.
    Should run daily (or more frequently for stock updates).
    """
    logger.info("[PRODUCT-SYNC] Starting product metrics sync...")
    
    db = SessionLocal()
    
    try:
        # Get all active products
        products = db.query(Ad).filter(Ad.status == 'active').all()
        logger.info(f"[PRODUCT-SYNC] Processing {len(products)} active products...")
        
        # Calculate date ranges
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        two_weeks_ago = now - timedelta(days=14)
        
        # Valid order statuses
        valid_statuses = ['paid', 'shipped', 'delivered']
        
        synced = 0
        for product in products:
            try:
                # Get or create ProductForecast record
                pf = db.query(ProductForecast).filter(
                    ProductForecast.mlb_id == product.id
                ).first()
                
                if not pf:
                    pf = ProductForecast(mlb_id=product.id)
                    db.add(pf)
                
                # Update basic info
                pf.title = product.title
                pf.sku = product.sku
                pf.category_ml = product.category_name
                pf.price = Decimal(str(product.price)) if product.price else Decimal('0')
                pf.cost = Decimal(str(product.cost)) if product.cost else Decimal('0')
                
                # Calculate margin
                if pf.price and pf.cost and pf.price > 0:
                    pf.margin_pct = ((pf.price - pf.cost) / pf.price * 100)
                
                # Calculate sales metrics - Last 7 days
                sales_7d = db.query(
                    func.sum(MlOrderItem.quantity).label('qty'),
                    func.sum(MlOrderItem.unit_price * MlOrderItem.quantity).label('revenue')
                ).join(MlOrder).filter(
                    MlOrderItem.ml_item_id == product.id,
                    MlOrder.date_closed >= week_ago,
                    MlOrder.status.in_(valid_statuses)
                ).first()
                
                pf.total_units_7d = sales_7d.qty or 0
                pf.total_revenue_7d = Decimal(str(sales_7d.revenue or 0))
                pf.avg_units_7d = Decimal(str((pf.total_units_7d or 0) / 7))
                
                # Calculate sales metrics - Last 30 days
                sales_30d = db.query(
                    func.sum(MlOrderItem.quantity).label('qty'),
                    func.sum(MlOrderItem.unit_price * MlOrderItem.quantity).label('revenue')
                ).join(MlOrder).filter(
                    MlOrderItem.ml_item_id == product.id,
                    MlOrder.date_closed >= month_ago,
                    MlOrder.status.in_(valid_statuses)
                ).first()
                
                pf.total_units_30d = sales_30d.qty or 0
                pf.total_revenue_30d = Decimal(str(sales_30d.revenue or 0))
                pf.avg_units_30d = Decimal(str((pf.total_units_30d or 0) / 30))
                
                # Calculate trend (compare last 7d vs previous 7d)
                prev_week_sales = db.query(
                    func.sum(MlOrderItem.quantity).label('qty')
                ).join(MlOrder).filter(
                    MlOrderItem.ml_item_id == product.id,
                    MlOrder.date_closed >= two_weeks_ago,
                    MlOrder.date_closed < week_ago,
                    MlOrder.status.in_(valid_statuses)
                ).scalar() or 0
                
                if prev_week_sales > 0:
                    pf.trend_pct = Decimal(str(((pf.total_units_7d - prev_week_sales) / prev_week_sales) * 100))
                    if pf.trend_pct > 10:
                        pf.trend = 'up'
                    elif pf.trend_pct < -10:
                        pf.trend = 'down'
                    else:
                        pf.trend = 'stable'
                else:
                    pf.trend_pct = Decimal('0')
                    pf.trend = 'stable' if pf.total_units_7d == 0 else 'up'
                
                # Stock info (from Ad table)
                pf.stock_current = product.available_quantity or 0
                pf.stock_full = 0  # TODO: Get from Full inventory if available
                
                # Calculate days of coverage
                if pf.avg_units_7d and pf.avg_units_7d > 0:
                    pf.days_of_coverage = Decimal(str(pf.stock_current)) / pf.avg_units_7d
                else:
                    pf.days_of_coverage = Decimal('999')  # No sales = infinite coverage
                
                # Determine stock status
                if pf.stock_current == 0:
                    pf.stock_status = 'stockout'
                    pf.has_rupture_risk = True
                elif pf.days_of_coverage < 3:
                    pf.stock_status = 'critical'
                    pf.has_rupture_risk = True
                elif pf.days_of_coverage < 7:
                    pf.stock_status = 'low'
                    pf.has_rupture_risk = True
                else:
                    pf.stock_status = 'ok'
                    pf.has_rupture_risk = False
                
                # Calculate today's forecast
                # Simple: avg_units_7d * temporal_factors (to be enhanced)
                stock_factor = 1.0 if pf.stock_current > 0 else 0.0
                if pf.stock_current > 0 and pf.days_of_coverage and pf.days_of_coverage < 1:
                    stock_factor = float(pf.days_of_coverage)
                
                pf.forecast_units_today = pf.avg_units_7d * Decimal(str(stock_factor))
                pf.forecast_revenue_today = pf.forecast_units_today * pf.price if pf.price else Decimal('0')
                
                pf.is_active = True
                pf.updated_at = datetime.utcnow()
                
                synced += 1
                
            except Exception as e:
                logger.error(f"[PRODUCT-SYNC] Error processing {product.id}: {e}")
                continue
        
        # Calculate ABC curve after all products are updated
        _calculate_abc_curve(db)
        
        db.commit()
        logger.info(f"[PRODUCT-SYNC] Synced {synced} products successfully")
        
        return {"status": "ok", "synced": synced}
        
    except Exception as e:
        logger.error(f"[PRODUCT-SYNC] Sync failed: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def _calculate_abc_curve(db):
    """
    Calculate ABC curve based on revenue.
    A: Top 80% of revenue
    B: Next 15%
    C: Bottom 5%
    """
    try:
        # Get all products ordered by revenue
        products = db.query(ProductForecast).filter(
            ProductForecast.is_active == True
        ).order_by(ProductForecast.total_revenue_30d.desc()).all()
        
        if not products:
            return
        
        # Calculate total revenue
        total_revenue = sum(float(p.total_revenue_30d or 0) for p in products)
        
        if total_revenue == 0:
            for p in products:
                p.curve = 'C'
                p.curve_criteria = 'revenue'
            return
        
        # Assign curves
        cumulative = 0
        for p in products:
            cumulative += float(p.total_revenue_30d or 0)
            pct = cumulative / total_revenue
            
            if pct <= 0.80:
                p.curve = 'A'
            elif pct <= 0.95:
                p.curve = 'B'
            else:
                p.curve = 'C'
            p.curve_criteria = 'revenue'
            
        logger.info(f"[PRODUCT-SYNC] ABC curve calculated for {len(products)} products")
        
    except Exception as e:
        logger.error(f"[PRODUCT-SYNC] Error calculating ABC curve: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = sync_product_metrics()
    print(f"Result: {result}")
