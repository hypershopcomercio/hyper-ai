
from flask import jsonify
from sqlalchemy import func, desc, asc

from datetime import datetime, timedelta
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.sale import Sale
from app.models.metric import Metric
from app.models.alert import Alert

@api_bp.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    from flask import request
    db = SessionLocal()
    try:
        # Filter Logic
        days_param = request.args.get('days', '7')
        days = int(days_param) if days_param.isdigit() else 7
        
        today = datetime.now().date()
        
        if days == 1:
            start_date = today
            prev_start_date = today - timedelta(days=1)
            period_label = "Hoje"
        else:
            start_date = today - timedelta(days=days)
            prev_start_date = start_date - timedelta(days=days)
            period_label = f"Últimos {days} dias"

        # 1. KPI: Total Active Ads
        total_ads = db.query(Ad).filter(Ad.status == 'active').count()
        
        # 2. KPI: Visits (Dynamic Period)
        from app.models.ml_metrics_daily import MlMetricsDaily
        
        # Current Period Visits
        visits_current = db.query(func.sum(MlMetricsDaily.visits)).filter(
            MlMetricsDaily.date >= start_date
        ).scalar() or 0
        
        # Previous Period Visits (for trend)
        if days == 1:
             visits_prev = db.query(func.sum(MlMetricsDaily.visits)).filter(
                MlMetricsDaily.date == prev_start_date
            ).scalar() or 0
        else:
            visits_prev = db.query(func.sum(MlMetricsDaily.visits)).filter(
                MlMetricsDaily.date >= prev_start_date,
                MlMetricsDaily.date < start_date
            ).scalar() or 0
        
        visits_trend = 0.0
        if visits_prev > 0:
            visits_trend = ((visits_current - visits_prev) / visits_prev) * 100

        # 3. KPI: Revenue & Sales (Dynamic Period)
        # Using Sale table for accuracy
        start_datetime = datetime.combine(start_date, datetime.min.time())
        prev_start_datetime = datetime.combine(prev_start_date, datetime.min.time())
        end_prev_datetime = start_datetime
        
        sales_current_sum = db.query(func.sum(Sale.total_amount)).filter(Sale.date_created >= start_datetime).scalar() or 0.0
        sales_count_current = db.query(Sale).filter(Sale.date_created >= start_datetime).count()
        
        # Previous Period Sales
        if days == 1:
            # For 'today', previous is 'yesterday' full day? or up to same time? simplified to full day yesterday
             sales_prev_sum = db.query(func.sum(Sale.total_amount)).filter(
                Sale.date_created >= prev_start_datetime,
                Sale.date_created < end_prev_datetime
            ).scalar() or 0.0
        else:
            sales_prev_sum = db.query(func.sum(Sale.total_amount)).filter(
                Sale.date_created >= prev_start_datetime,
                Sale.date_created < end_prev_datetime
            ).scalar() or 0.0
        
        revenue_trend = 0.0
        if sales_prev_sum > 0:
            revenue_trend = ((sales_current_sum - sales_prev_sum) / sales_prev_sum) * 100
            
        # 4. KPI: Average Margin
        avg_margin = db.query(func.avg(Ad.margin_percent)).filter(Ad.margin_percent != None, Ad.status == 'active').scalar() or 0.0
        
        # 5. Alerts
        low_stock_ads = db.query(Ad).filter(Ad.days_of_stock < 15, Ad.status == 'active').count()
        critical_alerts = 0
        
        # Total Revenue (Lifetime/All time in DB)
        total_revenue_all = db.query(func.sum(Sale.total_amount)).scalar() or 0.0

        # --- NEW: Actionable Lists for Widgets ---
        # 1. Trending Up (Winners)
        top_gainers = db.query(Ad).filter(Ad.status == 'active', Ad.visits_7d_change > 0).order_by(desc(Ad.visits_7d_change)).limit(5).all()
        # 2. Trending Down (Losers)
        top_losers = db.query(Ad).filter(Ad.status == 'active', Ad.visits_7d_change < 0).order_by(asc(Ad.visits_7d_change)).limit(5).all()
        # 3. Stock Risk
        stock_risks = db.query(Ad).filter(Ad.status == 'active', Ad.days_of_stock < 30, Ad.days_of_stock > 0).order_by(asc(Ad.days_of_stock)).limit(5).all()
        
        def serialize_min(ad_list):
            return [{
                "id": a.id,
                "title": a.title,
                "thumbnail": a.thumbnail,
                "value": a.visits_7d_change if hasattr(a, 'visits_7d_change') else None,
                "days_stock": a.days_of_stock,
                "price": a.price
            } for a in ad_list]

        return jsonify({
            "total_ads": total_ads,
            "visits_7d": visits_current, # Map current period to response key
            "visits_trend": round(visits_trend, 2),
            "revenue_7d": sales_current_sum, # Map current period to response key
            "revenue_trend": round(revenue_trend, 2),
            "sales_count_7d": sales_count_current, # Map current period to response key
            "average_margin": round(avg_margin, 2),
            "low_stock_ads": low_stock_ads,
            "critical_alerts": critical_alerts,
            "total_revenue_db": total_revenue_all,
            "period_label": period_label, # Pass back label for UI
            
            # Widget Data
            "top_gainers": serialize_min(top_gainers),
            "top_losers": serialize_min(top_losers),
            "stock_risks": serialize_min(stock_risks)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
