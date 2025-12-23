from flask import jsonify, request
from app.api import api_bp
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
from datetime import datetime, timedelta, timezone
import os

@api_bp.route('/debug/orders-test', methods=['GET'])
def debug_orders_test():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        seller_id = service.get_seller_id() if hasattr(service, 'get_seller_id') else None
        
        # Fallback if method doesn't exist on service (it's in SyncEngine normally)
        if not seller_id:
             from app.models.oauth_token import OAuthToken
             token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
             seller_id = token.user_id if token else "Unknown"

        # Timezone: Brasilia (UTC-3)
        # "Hoje" in Brasilia
        tz_offset = timezone(timedelta(hours=-3))
        now = datetime.now(tz_offset)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Convert to ISO with Offset for API? 
        # API expects ISO. usually UTC or Offset.
        # Start of Day in UTC:
        # If it is 00:00 -03:00, that is 03:00 UTC.
        start_iso = start_of_day.isoformat()
        now_iso = now.isoformat()
        
        print(f"DEBUG: Fetching from {start_iso} to {now_iso}")
        
        # Call API directly
        # service.get_orders supports date_from/to
        # ensure get_orders passes the params correctly
        # MeliApiService.get_orders signature: (seller_id, item_id, date_from, date_to)
        
        orders = service.get_orders(seller_id, date_from=start_iso, date_to=now_iso)
        
        total_amount = 0.0
        total_orders = 0
        paid_orders = 0
        
        results = []
        for o in orders:
            total_orders += 1
            if o.get("status") == "paid":
                paid_orders += 1
                total_amount += float(o.get("total_amount", 0))
            
            # Serialize for response
            results.append({
                "id": o.get("id"),
                "status": o.get("status"),
                "total": o.get("total_amount"),
                "date": o.get("date_created"),
                "date_closed": o.get("date_closed")
            })
            
        return jsonify({
            "debug": True,
            "periodo": { "from": start_iso, "to": now_iso },
            "apiResponse": {
                "total_encontrado": len(orders),
                "pedidos_pagos": paid_orders,
                "valor_total": total_amount
            },
            "all_ids": [str(o.get('id')) for o in orders], # Return ALL IDs for comparison
            "primeiros_pedidos": results[:10] 
        })
        
    except Exception as e:
        return jsonify({ "error": str(e) }), 500
    finally:
        db.close()

@api_bp.route('/debug/timezone', methods=['GET'])
def debug_timezone():
    now = datetime.now()
    tz_br = timezone(timedelta(hours=-3))
    now_br = datetime.now(tz_br)
    
    return jsonify({
        "server_time_utc_naive": now.isoformat(),
        "server_local_br": now_br.isoformat(),
        "env_tz": os.environ.get("TZ", "Not Set"),
        "today_utc_start": now.replace(hour=0,minute=0,second=0,microsecond=0).isoformat(),
        "today_br_start": now_br.replace(hour=0,minute=0,second=0,microsecond=0).isoformat()
    })
