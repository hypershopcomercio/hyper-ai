from flask import jsonify, request
from sqlalchemy import select, func, desc
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.sale import Sale
from . import api_bp

def get_db():
    return SessionLocal()

@api_bp.route("/ads", methods=["GET"])
def list_ads():
    db = get_db()
    try:
        # Params
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        status = request.args.get("status")
        query = request.args.get("q")
        sort_by = request.args.get("sort_by", "visits") # visits, sales, price

        stmt = select(Ad)
        
        # Filter
        if status:
            stmt = stmt.where(Ad.status == status)
        if query:
            stmt = stmt.where(Ad.title.ilike(f"%{query}%"))
            
        # Sort
        if sort_by == "visits":
            stmt = stmt.order_by(desc(Ad.total_visits))
        elif sort_by == "sales":
            stmt = stmt.order_by(desc(Ad.sold_quantity))
        elif sort_by == "price_asc":
            stmt = stmt.order_by(Ad.price)
        elif sort_by == "price_desc":
            stmt = stmt.order_by(desc(Ad.price))
            
        # Pagination
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)
        
        results = db.execute(stmt).scalars().all()
        
        data = []
        for ad in results:
            data.append({
                "id": ad.id,
                "title": ad.title,
                "price": ad.price,
                "status": ad.status,
                "inventory": ad.available_quantity,
                "sold_quantity": ad.sold_quantity,
                "thumbnail": ad.thumbnail,
                "total_visits": ad.total_visits,
                "cost": ad.cost,
                # Simple conversion rate calc
                "conversion_rate": (ad.sold_quantity / ad.total_visits) if ad.total_visits and ad.total_visits > 0 else 0
            })
            
        return jsonify(data)
    finally:
        db.close()

@api_bp.route("/ads/<ad_id>", methods=["GET"])
def get_ad_detail(ad_id):
    db = get_db()
    try:
        ad = db.execute(select(Ad).where(Ad.id == ad_id)).scalar_one_or_none()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
            
        return jsonify({
            "id": ad.id,
            "title": ad.title,
            "price": ad.price,
            "permalink": ad.permalink,
            "thumbnail": ad.thumbnail,
            "status": ad.status,
            "available_quantity": ad.available_quantity,
            "sold_quantity": ad.sold_quantity,
            "total_visits": ad.total_visits,
            "tiny_id": ad.tiny_id,
            "cost": ad.cost,
            "weight_g": ad.weight_g,
            "updated_at": ad.updated_at
        })
    finally:
        db.close()

@api_bp.route("/dashboard/metrics", methods=["GET"])
def dashboard_metrics():
    db = get_db()
    try:
        # Aggregates
        total_ads = db.query(func.count(Ad.id)).scalar()
        total_visits = db.query(func.sum(Ad.total_visits)).scalar() or 0
        total_sales_count = db.query(func.sum(Ad.sold_quantity)).scalar() or 0 # Using Ad.sold_quantity for simplicity or count Sales table
        
        # Real sales table count for robust data if needed
        # total_sales_db = db.query(func.count(Sale.id)).scalar()
        
        return jsonify({
            "total_ads": total_ads,
            "total_visits": total_visits,
            "total_sales": total_sales_count,
            "conversion_rate_global": (total_sales_count / total_visits) if total_visits > 0 else 0
        })
    finally:
        db.close()
