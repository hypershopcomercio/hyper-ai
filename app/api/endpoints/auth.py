
from flask import Blueprint, redirect, request, jsonify
from app.services.meli_auth import MeliAuthService
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
from datetime import datetime
from app.api import api_bp

auth_service = MeliAuthService()

@api_bp.route('/auth/ml', methods=['GET'])
def get_auth_url():
    """Generates URL and redirects to Mercado Livre Auth"""
    url = auth_service.get_auth_url()
    return redirect(url)

@api_bp.route('/auth/ml/callback', methods=['POST'])
def handle_callback():
    """Handles callback from frontend (which got code from ML)"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("=== ML CALLBACK RECEIVED ===")
    
    data = request.json
    logger.info(f"Request data: {data}")
    
    code = data.get('code') if data else None
    if not code:
        logger.error("No code in request")
        return jsonify({"error": "No code provided"}), 400
    
    logger.info(f"Code received: {code[:20]}...")
    
    try:
        # Exchange code for tokens
        logger.info("Exchanging code for tokens...")
        token_data = auth_service.exchange_code_for_token(code)
        logger.info(f"Token exchange successful. User ID: {token_data.get('user_id')}")
        
        # Save tokens
        logger.info("Saving tokens to database...")
        auth_service.save_tokens(token_data)
        logger.info("Tokens saved successfully!")
        
        return jsonify({"message": "Authentication successful", "success": True})
    except Exception as e:
        logger.error(f"Callback error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api_bp.route('/auth/ml/status', methods=['GET'])
def get_auth_status():
    """Returns connection status"""
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
