
from flask import jsonify, request
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

@api_bp.route('/settings', methods=['GET'])
def get_settings():
    db = SessionLocal()
    try:
        settings = db.query(SystemConfig).all()
        results = {}
        for s in settings:
            results[s.key] = {
                "value": s.value,
                "description": s.description,
                "group": s.group
            }
        return jsonify(results)
    finally:
        db.close()

@api_bp.route('/settings', methods=['POST'])
def update_settings():
    db = SessionLocal()
    try:
        data = request.json
        # Expected { "key": "value" }
        for key, value in data.items():
            setting = db.query(SystemConfig).filter(SystemConfig.key == key).first()
            if setting:
                setting.value = str(value)
            else:
                # Create if not exists
                setting = SystemConfig(key=key, value=str(value), group="general")
                db.add(setting)
            
        db.commit()
        return jsonify({"message": "Settings updated"})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
