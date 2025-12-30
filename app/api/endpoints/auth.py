
from flask import Blueprint, redirect, request, jsonify
from app.services.meli_auth import MeliAuthService
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
from datetime import datetime, timedelta
from app.api import api_bp
import jwt
import hashlib
import logging
from functools import wraps

logger = logging.getLogger(__name__)
auth_service = MeliAuthService()

# JWT Config
JWT_SECRET = "hyper-ai-secret-key-2025-gWh28dGcMp"
JWT_EXPIRATION_HOURS = 24


def generate_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"success": False, "error": "Token missing"}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        request.user_id = payload.get("user_id")
        request.user_email = payload.get("email")
        request.user_role = payload.get("role")
        return f(*args, **kwargs)
    return decorated


@api_bp.route('/auth/ml', methods=['GET'])
def get_auth_url():
    """Generates URL and redirects to Mercado Livre Auth"""
    url = auth_service.get_auth_url()
    return redirect(url)

@api_bp.route('/auth/ml/callback', methods=['POST'])
def handle_callback():
    """Handles callback from frontend (which got code from ML)"""
    logger.info("=== ML CALLBACK RECEIVED ===")
    
    data = request.json
    logger.info(f"Request data: {data}")
    
    code = data.get('code') if data else None
    if not code:
        logger.error("No code in request")
        return jsonify({"error": "No code provided"}), 400
    
    logger.info(f"Code received: {code[:20]}...")
    
    try:
        logger.info("Exchanging code for tokens...")
        token_data = auth_service.exchange_code_for_token(code)
        logger.info(f"Token exchange successful. User ID: {token_data.get('user_id')}")
        
        logger.info("Saving tokens to database...")
        auth_service.save_tokens(token_data)
        logger.info("Tokens saved successfully!")
        
        return jsonify({"message": "Authentication successful", "success": True})
    except Exception as e:
        logger.error(f"Callback error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api_bp.route('/auth/ml/status', methods=['GET'])
def get_auth_status():
    """Returns ML connection status"""
    db = SessionLocal()
    try:
        token = db.query(OAuthToken).filter_by(provider="mercadolivre").first()
        if not token:
             return jsonify({
                "connected": False,
                "message": "Not connected"
            })
            
        is_expired = False
        if token.expires_at and token.expires_at < datetime.now():
            is_expired = True

        return jsonify({
            "connected": True,
            "seller_id": token.seller_id,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "is_expired": is_expired
        })
    finally:
        db.close()


# ==================== USER LOGIN ====================

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    from app.models.user import User
    
    db = SessionLocal()
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email e senha obrigatórios"}), 400
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not user.verify_password(password):
            return jsonify({"success": False, "error": "Credenciais inválidas"}), 401
        
        if not user.is_active:
            return jsonify({"success": False, "error": "Usuário desativado"}), 401
        
        user.last_login = datetime.utcnow()
        db.commit()
        
        token = generate_token(user.id, user.email, user.role)
        
        return jsonify({
            "success": True,
            "data": {
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/auth/verify', methods=['GET'])
def verify_auth():
    """Verify if token is valid"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        return jsonify({"success": False, "valid": False}), 401
    
    payload = verify_token(token)
    if not payload:
        return jsonify({"success": False, "valid": False}), 401
    
    return jsonify({
        "success": True,
        "valid": True,
        "user": {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
    })
