
from flask import jsonify, request
from sqlalchemy import desc
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.alert import Alert

@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    db = SessionLocal()
    try:
        severity = request.args.get('severity')
        type_ = request.args.get('type')
        status = request.args.get('status', 'active') # Default active
        
        query = db.query(Alert)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        if type_:
            query = query.filter(Alert.type == type_)
        if status:
            query = query.filter(Alert.status == status)
            
        alerts = query.order_by(Alert.severity == 'critical', desc(Alert.created_at)).all()
        
        results = []
        for a in alerts:
            results.append({
                "id": a.id,
                "created_at": a.created_at.isoformat(),
                "severity": a.severity,
                "type": a.type,
                "message": a.message,
                "status": a.status,
                "ad_id": a.ad_id
            })
            
        return jsonify(results)
    finally:
        db.close()

@api_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
            
        alert.status = 'resolved'
        db.commit()
        return jsonify({"message": "Alert resolved"})
    finally:
        db.close()
