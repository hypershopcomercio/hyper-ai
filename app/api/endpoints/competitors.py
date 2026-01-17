
from flask import jsonify, request
from app.api import api_bp
from app.core.database import SessionLocal
from app.services.competition_engine import CompetitionEngine

@api_bp.route('/ads/<ad_id>/competitors', methods=['GET'])
def list_competitors(ad_id):
    db = SessionLocal()
    try:
        engine = CompetitionEngine(db)
        competitors = engine.get_competitors(ad_id)
        
        data = []
        for c in competitors:
            data.append({
                "id": c.competitor_id,
                "internal_id": c.id,
                "title": c.title,
                "price": c.price,
                "original_price": c.original_price,
                "permalink": c.permalink,
                "status": c.status,
                "last_updated": c.last_updated.isoformat() if c.last_updated else None
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ads/<ad_id>/competitors', methods=['POST'])
def add_competitor(ad_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400
            
        engine = CompetitionEngine(db)
        comp = engine.add_competitor(ad_id, url)
        
        return jsonify({
            "id": comp.competitor_id,
            "internal_id": comp.id,
            "title": comp.title,
            "price": comp.price,
            "original_price": comp.original_price,
            "status": comp.status
        }), 201
        
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        # Log error
        print(f"Error adding competitor: {e}")
        return jsonify({"error": "Failed to add competitor"}), 500
    finally:
        db.close()

@api_bp.route('/ads/<ad_id>/competitors/sync', methods=['POST'])
def sync_competitors(ad_id):
    db = SessionLocal()
    try:
        engine = CompetitionEngine(db)
        updated_count = engine.update_competitor_prices(ad_id)
        
        return jsonify({
            "message": "Update completed",
            "updated_count": updated_count
        })
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
        db.close()
