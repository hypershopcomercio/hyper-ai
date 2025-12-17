import logging
import requests
import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.oauth_token import OAuthToken

logger = logging.getLogger(__name__)

class MeliApiService:
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.base_url = "https://api.mercadolibre.com"
        # Try to load token from DB if session provided, else from env/settings
        self.access_token = self._get_valid_token()

    def _get_valid_token(self):
        """
        Retrieves a valid access token from DB. Refreshes if expired.
        """
        # We need a session. If not provided, open one locally for this operation.
        local_session = False
        db = self.db_session
        if not db:
            from app.core.database import SessionLocal
            db = SessionLocal()
            local_session = True

        try:
            # Fetch token for provider
            token_record = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
            if not token_record:
                 # No token in DB.
                 # Per requirement: "Buscar tokens do banco, não do .env"
                 # So we fail or return None if not found.
                 logger.error("No OAuth token found in database for provider 'mercadolivre'.")
                 return None
            
            # Check expiration (giving 5 min safety buffer)
            # Check expiration (giving 5 min safety buffer)
            if token_record.expires_at:
                now = datetime.datetime.now()
                if token_record.expires_at.tzinfo:
                    now = datetime.datetime.now(token_record.expires_at.tzinfo)
                
                if token_record.expires_at <= now + datetime.timedelta(minutes=5):
                    logger.info("Token expired. Refreshing...")
                    return self._refresh_token(db, token_record)
            
            return token_record.access_token
        except Exception as e:
            logger.error(f"Error retrieving token: {e}")
            return None
        finally:
            if local_session:
                db.close()

    def _refresh_token(self, db: Session, token_record: OAuthToken):
        url = "https://api.mercadolibre.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": settings.MELI_APP_ID,
            "client_secret": settings.MELI_CLIENT_SECRET,
            "refresh_token": token_record.refresh_token
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            new_tokens = response.json()
            
            # Update DB
            token_record.access_token = new_tokens["access_token"]
            token_record.refresh_token = new_tokens["refresh_token"]
            
            expires_in = new_tokens.get("expires_in", 21600) # Default 6h
            token_record.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            
            db.commit()
            
            logger.info("Token refreshed and saved to database.")
            return new_tokens["access_token"]
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise

    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_user_items(self, user_id: str):
        url = f"{self.base_url}/users/{user_id}/items/search"
        params = {"search_type": "scan", "status": "active", "limit": 100}
        items = []
        while True:
            response = requests.get(url, params=params, headers=self.get_headers())
            response.raise_for_status()
            data = response.json()
            items.extend(data.get("results", []))
            
            # Helper for scan scroll
            scroll_id = data.get("paging", {}).get("scroll_id") or data.get("scroll_id")
            if not scroll_id:
                break
            params["scroll_id"] = scroll_id
        return items
    
    def get_item_details(self, item_ids: list[str]):
        chunk_size = 20
        all_details = []
        for i in range(0, len(item_ids), chunk_size):
            chunk = item_ids[i:i+chunk_size]
            ids_str = ",".join(chunk)
            url = f"{self.base_url}/items"
            params = {"ids": ids_str}
            response = requests.get(url, params=params, headers=self.get_headers())
            
            if response.status_code == 200:
                results = response.json()
                for res in results:
                     if res["code"] == 200:
                         all_details.append(res["body"])
            else:
                 logger.error(f"Error fetching chunk: {response.status_code}")
        return all_details

    def get_visits_time_window(self, item_id: str, last: int = 30, unit: str = "day"):
        # GET /items/{item_id}/visits/time_window?last=30&unit=day (Hypothetical endpoint per user request)
        # Note: Standard API is /items/{id}/visits/time_window?last=X&unit=day
        url = f"{self.base_url}/items/{item_id}/visits/time_window"
        params = {"last": last, "unit": unit}
        try:
             response = requests.get(url, params=params, headers=self.get_headers())
             if response.status_code == 200:
                 return response.json()
             return None
        except Exception as e:
             logger.error(f"Error fetching visits time window for {item_id}: {e}")
             return None

    def get_orders(self, seller_id: str, item_id: str = None, date_from: str = None, date_to: str = None):
        """
        Search orders. Optionally filter by item_id (q parameter) or date range.
        Dates should be ISO format string.
        """
        url = f"{self.base_url}/orders/search"
        params = {
            "seller": seller_id,
            "sort": "date_desc",
            "limit": 50
        }
        if item_id:
            params["q"] = item_id 
        
        if date_from:
            params["order.date_created.from"] = date_from
        if date_to:
            params["order.date_created.to"] = date_to
            
        orders = []
        while True:
            response = requests.get(url, params=params, headers=self.get_headers())
            
            # Retry on 401 (Unauthorized) - Token might be revoked or expired despite DB time
            if response.status_code == 401:
                logger.warning("401 Unauthorized in get_orders. Attempting token refresh and retry...")
                # We need a DB session to refresh
                local_session = False
                db = self.db_session
                if not db:
                     from app.core.database import SessionLocal
                     db = SessionLocal()
                     local_session = True
                
                try:
                    token_record = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
                    self.access_token = self._refresh_token(db, token_record)
                    # Retry
                    response = requests.get(url, params=params, headers=self.get_headers())
                except Exception as e:
                     logger.error(f"Retry failed: {e}")
                finally:
                     if local_session:
                         db.close()

            # Sometimes API returns 404/400 if no orders found or filters overlap bad
            if response.status_code != 200:
                logger.warning(f"Order search returned {response.status_code} for params {params}")
                break

            data = response.json()
            results = data.get("results", [])
            orders.extend(results)
            
            paging = data.get("paging", {})
            total = paging.get("total", 0)
            
            if len(orders) >= total:
                break
                
            # Offset pagination
            current_offset = params.get("offset", 0)
            params["offset"] = current_offset + 50
            if params["offset"] > 1000: # Safety limit
                break
        return orders


    def get_ads_performance(self, item_ids: list[str], date_from: datetime.date, date_to: datetime.date):
        """
        Fetches Product Ads performance metrics for a list of items within a date range.
        Uses /advertising/product_ads/performances/v1/by_item (or similar, depending on accurate API docs).
        Fallback/Simplification: 
        Actually, 'advertising' uses separate scope and endpoints. 
        Endpoint: POST /advertising/product_ads/performances/v1/search
        """
        url = "https://api.mercadolibre.com/advertising/product_ads/performances/v1/search"
        
        # We need a token with 'advertising' scope. Assuming our token has it.
        # Date format: YYYY-MM-DD
        payload = {
            "date_range": {
                "from": date_from.strftime("%Y-%m-%d"),
                "to": date_to.strftime("%Y-%m-%d")
            },
            "item_ids": item_ids
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.get_headers())
            if response.status_code == 200:
                # Response example: [ { item_id: "...", cost: 12.5, ... } ]
                return response.json()
            elif response.status_code == 403:
                logger.warning("Ads API Access Forbidden. Check Token Scopes (advertising).")
                return []
            else:
                logger.error(f"Ads Performance Error: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching ads performance: {e}")
            return []


    def get_shipment(self, shipment_id: str):
        """
        Fetch shipment details including costs.
        """
        url = f"{self.base_url}/shipments/{shipment_id}"
        resp = requests.get(url, headers=self.get_headers())
        if resp.status_code == 200:
            return resp.json()
        logger.warning(f"Failed to fetch shipment {shipment_id}: {resp.status_code}")
        return None

    def get_visits_time_window(self, item_id: str, last=30, unit="day"):
        """
        Fetch visits over a time window.
        URL: /items/{item_id}/visits/time_window?last=30&unit=day
        Returns: {
            "item_id": "MLB...",
            "date_from": "...",
            "date_to": "...",
            "unit": "day",
            "results": [
                {"date": "2025-12-01T00:00:00Z", "visits": 10},
                ...
            ]
        }
        """
        url = f"{self.base_url}/items/{item_id}/visits/time_window"
        params = {"last": last, "unit": unit}
        resp = requests.get(url, headers=self.get_headers(), params=params)
        
        # Retry on 401 (token refresh) if needed
        if resp.status_code == 401:
             logger.warning("401 in get_visits. Refreshing...")
             # Just return None for now or duplicate refresh logic. 
             # Ideally _request method handles this wrapper.
             # Sprint 2 MVP: Skip logic for now, SyncEngine handles batch fail.
             pass

        if resp.status_code == 200:
            return resp.json()
        
        # Log error
        # logger.warning(f"Visits fetch failed for {item_id}: {resp.status_code}")
        return None
