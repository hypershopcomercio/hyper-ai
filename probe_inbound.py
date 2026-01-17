
import os
import requests
import json
from app.core.config import settings
from app.services.meli_auth import MeliAuthService
from app.models.user import User
from app.core.database import SessionLocal

def get_access_token():
    auth_service = MeliAuthService()
    token = auth_service.get_valid_token()
    return token


def get_auth_info():
    db = SessionLocal()
    try:
        from app.models.oauth_token import OAuthToken
        token = db.query(OAuthToken).filter_by(provider="mercadolivre").first()
        if token:
           return token.access_token, token.seller_id
        return None, None
    finally:
        db.close()

def probe_endpoints():
    token, seller_id = get_auth_info()
    if not token:
        print("No token.")
        return

    headers = {'Authorization': f'Bearer {token}'}
    base_url = "https://api.mercadolibre.com"

    # Potential Endpoints for Inbound/Shipments
    endpoints = [
        f"/stock/fulfillment/inbound/shipments/search?seller_id={seller_id}&status=closed",
        f"/stock/fulfillment/inbound/shipments/search?seller_id={seller_id}",
    ]

    print(f"--- PROBING INBOUND ENDPOINTS (Seller {seller_id}) ---")
    for ep in endpoints:
        url = f"{base_url}{ep}"
        try:
            print(f"GET {ep} ...")
            resp = requests.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    print(json.dumps(data, indent=2)[:500]) # First 500 chars
                except:
                    print("Non-JSON response")
            elif resp.status_code == 403:
                print("403 Forbidden (Scope?)")
            else:
                print(f"Error: {resp.text[:200]}")
        except Exception as e:
            print(f"Exception: {e}")
        print("-" * 30)

if __name__ == "__main__":
    probe_endpoints()
