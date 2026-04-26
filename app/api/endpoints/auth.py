
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

@api_bp.route('/auth/ml/callback', methods=['GET', 'POST'])
def handle_callback():
    """Handles callback from ML (GET redirect) or frontend (POST with code)"""
    logger.info("=== ML CALLBACK RECEIVED ===")
    
    # Handle GET (direct redirect from ML)
    if request.method == 'GET':
        code = request.args.get('code')
        if not code:
            return "<h1>Erro</h1><p>Código não recebido do Mercado Livre</p>", 400
        
        logger.info(f"GET callback - Code received: {code[:20]}...")
        
        try:
            token_data = auth_service.exchange_code_for_token(code)
            logger.info(f"Token exchange successful. User ID: {token_data.get('user_id')}")
            
            auth_service.save_tokens(token_data)
            logger.info("Tokens saved successfully!")
            
            # Return success HTML page
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Autenticação Concluída</title>
                <style>
                    body { font-family: system-ui; background: linear-gradient(135deg, #1a1c2e, #12141e); color: white; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
                    .card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 48px; text-align: center; max-width: 400px; }
                    .icon { width: 64px; height: 64px; background: linear-gradient(135deg, #10b981, #059669); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 24px; font-size: 32px; }
                    h1 { margin: 0 0 8px; font-size: 24px; }
                    p { color: #94a3b8; margin: 0 0 24px; }
                    a { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-weight: 600; display: inline-block; }
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="icon">✓</div>
                    <h1>Autenticação Concluída!</h1>
                    <p>Sua conta do Mercado Livre foi conectada com sucesso.</p>
                    <a href="http://localhost:3000">Voltar ao Sistema</a>
                </div>
            </body>
            </html>
            """
        except Exception as e:
            logger.error(f"Callback error: {e}", exc_info=True)
            return f"<h1>Erro</h1><p>{str(e)}</p>", 500
    
    # Handle POST (from frontend)
    data = request.json
    logger.info(f"POST callback - Request data: {data}")
    
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
        
        response = jsonify({
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

        # Configurar Cookie de Autenticação
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,  # Segurança: impede que scripts maliciosos leiam o token
            secure=True,    # Segurança: só envia via HTTPS
            samesite="Lax",
            max_age=24 * 3600  # 24 horas
        )
        
        return response
        
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


@api_bp.route('/auth/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile (name)"""
    from app.models.user import User
    
    db = SessionLocal()
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({"success": False, "error": "Nome não pode estar vazio"}), 400
        
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            return jsonify({"success": False, "error": "Usuário não encontrado"}), 404
        
        user.name = name
        db.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        })
        
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/auth/password', methods=['PUT'])
@require_auth
def change_password():
    """Change user password"""
    from app.models.user import User
    
    db = SessionLocal()
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({"success": False, "error": "Preencha todos os campos"}), 400
        
        if len(new_password) < 6:
            return jsonify({"success": False, "error": "A nova senha deve ter pelo menos 6 caracteres"}), 400
        
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            return jsonify({"success": False, "error": "Usuário não encontrado"}), 404
        
        # Verify current password
        if not user.verify_password(current_password):
            return jsonify({"success": False, "error": "Senha atual incorreta"}), 401
        
        # Update password
        user.password_hash = User.hash_password(new_password)
        db.commit()
        
        return jsonify({"success": True, "message": "Senha alterada com sucesso"})
        
    except Exception as e:
        db.rollback()
        logger.error(f"Password change error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

