from flask import jsonify
from app.api import api_bp
from app.core.database import SessionLocal
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar a saúde do sistema e conexão com o banco."""
    health_status = {
        "status": "online",
        "database": "unknown",
        "timestamp": None
    }
    
    db = SessionLocal()
    try:
        # Tenta uma consulta simples no banco
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Health check database error: {e}")
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    finally:
        db.close()
        
    return jsonify(health_status)
