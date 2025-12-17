
from flask import jsonify, request
from sqlalchemy import desc
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.system_log import SystemLog

@api_bp.route('/logs', methods=['GET'])
def get_logs():
    db = SessionLocal()
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        module = request.args.get('module')
        level = request.args.get('level')
        
        query = db.query(SystemLog)
        
        if module:
            query = query.filter(SystemLog.module == module)
        if level:
            query = query.filter(SystemLog.level == level)
            
        total = query.count()
        logs = query.order_by(desc(SystemLog.timestamp)).offset(offset).limit(limit).all()
        
        results = []
        for log in logs:
            results.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "module": log.module,
                "level": log.level,
                "message": log.message,
                "details": log.details,
                "duration_ms": log.duration_ms
            })
            
        return jsonify({
            "total": total,
            "data": results,
            "limit": limit,
            "offset": offset
        })
    finally:
        db.close()
