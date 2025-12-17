
from flask import jsonify
from app.api import api_bp
from app.services.meli_auth import MeliAuthService
import requests

@api_bp.route('/debug/ml-test', methods=['GET'])
def test_ml_connection():
    auth = MeliAuthService()
    results = {
        "token_status": "unknown",
        "me_endpoint": None,
        "search_endpoint": None,
        "error": None
    }
    
    try:
        token = auth.get_valid_token()
        if not token:
            results["token_status"] = "missing_or_invalid"
            return jsonify(results)
        
        results["token_status"] = "valid_format"
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Users/Me
        try:
            me_res = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
            results["me_endpoint"] = {
                "status": me_res.status_code,
                "data": me_res.json() if me_res.status_code == 200 else me_res.text
            }
            seller_id = me_res.json().get("id")
        except Exception as e:
            results["me_endpoint"] = {"error": str(e)}
            seller_id = None
            
        # 2. Search Items
        if seller_id:
            try:
                url = f"https://api.mercadolibre.com/users/{seller_id}/items/search?limit=5"
                search_res = requests.get(url, headers=headers)
                results["search_endpoint"] = {
                    "status": search_res.status_code,
                    "url": url,
                    "data": search_res.json() if search_res.status_code == 200 else search_res.text
                }
            except Exception as e:
                results["search_endpoint"] = {"error": str(e)}
                
        return jsonify(results)
        
    except Exception as e:
        results["error"] = str(e)
        return jsonify(results), 500

@api_bp.route('/debug/db-test', methods=['GET'])
def test_db_connection():
    from sqlalchemy import text
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    results = {
        "database": {"connected": False, "name": "unknown", "time": None},
        "tables": {},
        "counts": {},
        "ml_token": {"exists": False}
    }
    
    try:
        # 1. Test Connection
        try:
            res = db.execute(text("SELECT NOW() as time, current_database() as db"))
            row = res.fetchone()
            results["database"] = {
                "connected": True,
                "name": row[1],
                "time": str(row[0])
            }
        except Exception as e:
            results["database"]["error"] = str(e)
            return jsonify(results), 500

        # 2. Check Tables (Mapping User requested 'sync.*' to actual 'public.*')
        # Structure: user_name -> actual_table
        table_map = {
            "ml_listings": "ads",
            "ml_daily_metrics": "metrics",
            "tiny_products": "tiny_products",
            "oauth_tokens": "oauth_tokens"
        }
        
        for key, table_name in table_map.items():
            try:
                # Check existence (in public schema)
                exists_query = text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}')")
                exists = db.execute(exists_query).scalar()
                results["tables"][key] = bool(exists)
                
                # Check count if exists
                if exists:
                    count = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                    results["counts"][key] = count
                else:
                    results["counts"][key] = 0
            except Exception as e:
                results["tables"][key] = f"Error: {e}"

        # 3. Check ML Token
        try:
            # Using raw SQL to avoid model dependency issues here
            token_res = db.execute(text("SELECT provider, seller_id, expires_at, created_at FROM oauth_tokens WHERE provider = 'mercadolivre'"))
            token = token_res.fetchone()
            
            if token:
                results["ml_token"] = {
                    "exists": True,
                    "seller_id": token[1],
                    "expires_at": str(token[2]),
                    "created_at": str(token[3])
                }
            else:
                results["ml_token"] = {"exists": False, "message": "No token with provider='mercadolivre' found"}
                
        except Exception as e:
            results["ml_token"]["error"] = str(e)

        return jsonify(results)
        
    except Exception as e:
        return jsonify({"fatal_error": str(e)}), 500
    finally:
        db.close()
