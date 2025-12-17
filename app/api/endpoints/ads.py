from flask import jsonify, request
from sqlalchemy import desc, asc
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ml_metrics_daily import MlMetricsDaily

@api_bp.route('/ads', methods=['GET'])
def get_ads():
    db = SessionLocal()
    try:
        query = db.query(Ad)
        
        # Filters
        status = request.args.get('status')
        if status:
            query = query.filter(Ad.status == status)
            
        search = request.args.get('search')
        if search:
            query = query.filter(Ad.title.ilike(f"%{search}%"))
            
        # Decision Filters
        filter_type = request.args.get('filter_type')
        if filter_type == 'stock_critical':
            # Critical Stock: Days of stock < 15 or Quantity < 5
            query = query.filter((Ad.days_of_stock < 15) | (Ad.available_quantity < 5))
            query = query.filter(Ad.status == 'active') # Only active ads
        elif filter_type == 'low_margin':
            # Low Margin: Less than 15%
            query = query.filter(Ad.margin_percent < 15)
            query = query.filter(Ad.status == 'active')
        elif filter_type == 'no_sales':
            # No Sales: Sales 30d is 0 or null
            query = query.filter((Ad.sales_30d == 0) | (Ad.sales_30d == None))
            query = query.filter(Ad.status == 'active')

            
        # Sorting
        sort_by = request.args.get('sort_by', 'updated_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        sort_column = getattr(Ad, sort_by, Ad.updated_at)
        if sort_order == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
            
        # Pagination
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        total = query.count()
        ads = query.offset(offset).limit(limit).all()
        
        results = []
        for ad in ads:
            results.append({
                "id": ad.id,
                "title": ad.title,
                "price": ad.price,
                "available_quantity": ad.available_quantity,
                "status": ad.status,
                "thumbnail": ad.thumbnail,
                "permalink": ad.permalink,
                "sku": ad.sku,
                
                # Metrics
                "visits_30d": ad.visits_30d,
                "sales_30d": ad.sales_30d,
                "visits_7d_change": ad.visits_7d_change,
                "sales_7d_change": ad.sales_7d_change,
                "days_of_stock": ad.days_of_stock,
                
                # Financials
                "cost": ad.cost,
                "margin_percent": ad.margin_percent,
                "margin_value": ad.margin_value,
                "is_margin_alert": ad.is_margin_alert,
                "updated_at": ad.updated_at.isoformat() if ad.updated_at else None
            })
            
        return jsonify({
            "total": total,
            "data": results,
            "limit": limit,
            "offset": offset
        })
    finally:
        db.close()

@api_bp.route('/ads/<ad_id>', methods=['GET'])
def get_ad_details(ad_id):
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
            
        # Get metrics history (last 30 days) from MlMetricsDaily
        metrics = db.query(MlMetricsDaily).filter(MlMetricsDaily.item_id == ad_id).order_by(MlMetricsDaily.date.asc()).limit(30).all()
        
        history = []
        for m in metrics:
            history.append({
                "date": m.date.isoformat(),
                "visits": m.visits,
                "sales": m.sales_qty,
                # conversion rate? m.conversion_rate or calc
                "revenue": m.sales_revenue
            })
            
        return jsonify({
            "id": ad.id,
            "title": ad.title,
            "price": ad.price,
            "status": ad.status,
            "thumbnail": ad.thumbnail,
            "available_quantity": ad.available_quantity,
            "permalink": ad.permalink,
            "sku": ad.sku,
            "history": history,
            
            "metrics": {
                "visits_30d": ad.visits_30d,
                "visits_7d_change": ad.visits_7d_change,
                "sales_7d_change": ad.sales_7d_change,
                "days_of_stock": ad.days_of_stock
            },
            
            "financials": {
                "cost": ad.cost,
                "margin_percent": ad.margin_percent,
                "margin_value": ad.margin_value,
                "is_margin_alert": ad.is_margin_alert,
                "commission_cost": ad.commission_cost,
                "shipping_cost": ad.shipping_cost,
                "tax_cost": ad.tax_cost,
                "ads_spend_30d": ad.ads_spend_30d
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
