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
                now = datetime.datetime.utcnow()
                expires_at = token_record.expires_at
                if expires_at.tzinfo:
                    expires_at = expires_at.replace(tzinfo=None)
                
                if expires_at <= now + datetime.timedelta(minutes=5):
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
            token_record.expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
            
            db.commit()
            
            logger.info("Token refreshed and saved to database.")
            return new_tokens["access_token"]
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise

    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def request(self, method: str, endpoint: str, params: dict = None, json_data: dict = None, timeout: int = 30, max_retries: int = 3, extra_headers: dict = None):
        """
        Generic request method with automatic token refresh and 429 (Rate Limit) retry.
        Endpoint should be relative, e.g. '/orders/search'
        extra_headers: merged over the auth header (e.g. Api-Version for /advertising/*)
        """
        import time
        url = f"{self.base_url}{endpoint}"

        def build_headers():
            h = self.get_headers()
            if extra_headers:
                h.update(extra_headers)
            return h

        retry_delay = 10 # seconds

        for attempt in range(max_retries + 1):
            try:
                # Use provided timeout
                resp = requests.request(method, url, headers=build_headers(), params=params, json=json_data, timeout=timeout)
                
                # Handle Rate Limit (429)
                if resp.status_code == 429:
                    if attempt < max_retries:
                        sleep_time = retry_delay * (attempt + 1)
                        logger.warning(f"Rate limit (429) hit for {endpoint}. Retrying in {sleep_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(sleep_time)
                        continue
                    else:
                        logger.error(f"Rate limit (429) persisted after {max_retries} retries for {endpoint}.")
                
                # Token Refresh on 401
                if resp.status_code == 401:
                    logger.warning(f"401 Unauthorized for {endpoint}. Refreshing token...")
                    
                    local_session = False
                    db = self.db_session
                    if not db:
                         from app.core.database import SessionLocal
                         db = SessionLocal()
                         local_session = True
                    
                    try:
                        token_record = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
                        if token_record:
                            self.access_token = self._refresh_token(db, token_record)
                            # Special case: allow ONE more attempt after refresh even if max_retries is 0
                            if attempt >= max_retries:
                                logger.info(f"Retrying {endpoint} once more after token refresh (fast mode override).")
                                resp = requests.request(method, url, headers=build_headers(), params=params, json=json_data, timeout=timeout)
                                return resp
                            continue
                        else:
                            logger.error("No token to refresh.")
                    except Exception as e:
                        logger.error(f"Refresh failed: {e}")
                    finally:
                        if local_session:
                            db.close()
                
                return resp
                
            except requests.RequestException as e:
                if attempt < max_retries:
                    logger.warning(f"Request error for {endpoint}: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                logger.error(f"Request Error for {endpoint} after {max_retries} retries: {e}")
                raise

    def get_user_items(self, user_id: str):
        endpoint = f"/users/{user_id}/items/search"
        params = {"search_type": "scan", "limit": 100}
        items = []
        while True:
            response = self.request('GET', endpoint, params=params)
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
            endpoint = "/items"
            params = {"ids": ids_str}
            response = self.request('GET', endpoint, params=params)
            
            if response.status_code == 200:
                results = response.json()
                for res in results:
                     if res["code"] == 200:
                         all_details.append(res["body"])
            else:
                 logger.error(f"Error fetching chunk: {response.status_code}")
        return all_details

    def get_visits_time_window(self, item_id: str, last: int = 30, unit: str = "day", ending: str = None):
        """
        Fetch visits for a specific time window.
        ending: Optional 'YYYY-MM-DD'. If not provided, defaults to today/now.
        """
        endpoint = f"/items/{item_id}/visits/time_window"
        params = {"last": last, "unit": unit}
        if ending:
            params["ending"] = ending
            
        try:
             response = self.request('GET', endpoint, params=params)
             if response.status_code == 200:
                 return response.json()
             return None
        except Exception as e:
             logger.error(f"Error fetching visits time window for {item_id}: {e}")
             return None

    def get_total_visits(self, item_id: str):
        """
        Fetches the total lifetime visits for an item.
        Reliable way: /items/{id}/visits which typically returns total.
        """
        try:
            response = self.request('GET', f"/items/{item_id}/visits")
            if response.status_code == 200:
                data = response.json()
                return data.get("total_visits", 0)
            return 0
        except Exception as e:
            logger.error(f"Error fetching total visits for {item_id}: {e}")
            return 0

    def get_item_pricing(self, item_id: str):
        """
        Fetches detailed pricing info to find active promotions.
        """
        try:
            response = self.request('GET', f"/items/{item_id}/prices")
            if response.status_code == 200:
                data = response.json()
                prices = data.get("prices", [])
                
                standard = next((p for p in prices if p.get("type") == "standard"), None)
                promotion = next((p for p in prices if p.get("type") == "promotion"), None)
                
                res = {"original_price": None, "promotion_price": None, "price": None}
                if standard: res["price"] = standard.get("amount")
                if promotion:
                    res["promotion_price"] = promotion.get("amount")
                    res["original_price"] = promotion.get("regular_amount") or (standard.get("amount") if standard else None)
                return res
            return None
        except Exception as e:
            logger.error(f"Error fetching pricing for {item_id}: {e}")
            return None

    def get_orders(self, seller_id: str, item_id: str = None, date_from: str = None, date_to: str = None):
        """
        Search orders with retry logic.
        """
        endpoint = "/orders/search"
        params = {"seller": seller_id, "sort": "date_desc", "limit": 50}
        if item_id: params["q"] = item_id 
        if date_from: params["order.date_created.from"] = date_from
        if date_to: params["order.date_created.to"] = date_to
            
        orders = []
        while True:
            response = self.request('GET', endpoint, params=params)
            if response.status_code != 200:
                logger.warning(f"Order search returned {response.status_code}")
                break

            data = response.json()
            results = data.get("results", [])
            orders.extend(results)
            
            paging = data.get("paging", {})
            total = paging.get("total", 0)
            if len(orders) >= total: break
                
            params["offset"] = params.get("offset", 0) + 50
            if params["offset"] > 1000: break
        return orders

    def get_order(self, order_id: str):
        """Fetch single order by ID."""
        resp = self.request('GET', f"/orders/{order_id}")
        if resp.status_code == 200: return resp.json()
        return None

    def get_advertiser_id(self, fast=False):
        """
        Gets the REAL advertiser_id for Product Ads via /advertising/advertisers.

        IMPORTANT: advertiser_id is NOT the seller_id. Confirmed in production:
        seller 1400902328 -> advertiser 347940. The old assumption poisoned the
        legacy cache key 'ml_advertiser_id', so this uses 'ml_advertiser_id_v2'.
        """
        db = self.db_session
        local_session = False
        if not db:
            from app.core.database import SessionLocal
            db = SessionLocal()
            local_session = True

        try:
            from app.models.system_config import SystemConfig

            # 1. Check cache (v2 key — legacy key held seller_id, which is wrong)
            cached = db.query(SystemConfig).filter_by(key="ml_advertiser_id_v2").first()
            if cached and cached.value:
                return cached.value

            # 2. Official source: advertisers endpoint (requires Api-Version: 1)
            response = self.request('GET', "/advertising/advertisers", params={"product_id": "PADS"},
                                    extra_headers={"Api-Version": "1"},
                                    timeout=5 if fast else 30,
                                    max_retries=0 if fast else 3)
            if response and response.status_code == 200:
                advertisers = response.json().get("advertisers", [])
                adv = next((a for a in advertisers if a.get("site_id") == "MLB"),
                           advertisers[0] if advertisers else None)
                if adv and adv.get("advertiser_id"):
                    advertiser_id = str(adv["advertiser_id"])
                    if cached:
                        cached.value = advertiser_id
                    else:
                        db.add(SystemConfig(key="ml_advertiser_id_v2", value=advertiser_id, group="cache"))
                    db.commit()
                    logger.info(f"Cached advertiser_id={advertiser_id} from /advertising/advertisers.")
                    return advertiser_id

            logger.error(f"Could not determine advertiser_id (status={response.status_code if response else 'no response'}).")
            return None
        except Exception as e:
            logger.error(f"Error getting advertiser_id: {e}")
            return None
        finally:
            if local_session:
                db.close()

    def get_ads_performance(self, item_ids: list[str] = None, date_from = None, date_to = None, fast=False):
        """
        Fetches Product Ads performance metrics for items.
        If fast=True, uses a very short timeout and 0 retries (ideal for dashboard load).
        """
        advertiser_id = self.get_advertiser_id(fast=fast)
        if not advertiser_id: return []
        
        endpoint = f"/advertising/MLB/advertisers/{advertiser_id}/product_ads/ads/search"
        
        d_from = date_from.strftime("%Y-%m-%d") if hasattr(date_from, 'strftime') else date_from
        d_to = date_to.strftime("%Y-%m-%d") if hasattr(date_to, 'strftime') else date_to
            
        params = {
            "date_from": d_from, "date_to": d_to,
            "metrics": "clicks,prints,cost,cpc,acos,roas,amount",
            "limit": 100
        }
        
        all_results = []
        offset = 0
        
        # Override timeout/retries if fast mode is requested
        request_timeout = 5 if fast else 30
        request_retries = 0 if fast else 3
        
        try:
            while True:
                params["offset"] = offset
                response = self.request('GET', endpoint, params=params, timeout=request_timeout,
                                        max_retries=request_retries, extra_headers={"Api-Version": "2"})
                if not response or response.status_code != 200: break
                
                data = response.json()
                results = data.get("results", [])
                all_results.extend(results)
                
                paging = data.get("paging", {})
                if len(all_results) >= paging.get("total", 0) or not results: break
                offset += len(results)
                if offset > 1000: break
            
            filtered = []
            item_ids_set = set(item_ids) if item_ids else None
            for ad in all_results:
                if not item_ids_set or ad.get("item_id") in item_ids_set:
                    m = ad.get("metrics", {})
                    filtered.append({
                        "item_id": ad.get("item_id"),
                        "cost": float(m.get("cost", 0) or 0),
                        "amount": float(m.get("amount", 0) or 0),
                        "clicks": int(m.get("clicks", 0) or 0),
                        "prints": int(m.get("prints", 0) or 0)
                    })
            return filtered
        except Exception as e:
            logger.error(f"Error fetching ads performance: {e}")
            return []

    # Metrics set for per-day persistence. units_quantity = units sold attributed
    # to Ads (direct + indirect). Some accounts/API versions reject the extended
    # set, so callers fall back to the base set on non-200.
    ADS_METRICS_BASE = "clicks,prints,cost,cpc,acos,roas,amount"
    ADS_METRICS_EXTENDED = ADS_METRICS_BASE + ",units_quantity,direct_units_quantity,indirect_units_quantity"

    def get_ads_performance_daily(self, day) -> list[dict]:
        """
        Fetches Product Ads per-item metrics for a SINGLE day (date_from == date_to),
        giving real daily granularity for persistence in ml_ads_item_daily.
        Returns [] on any failure (caller decides whether to retry the day later).
        """
        advertiser_id = self.get_advertiser_id()
        if not advertiser_id:
            return []

        endpoint = f"/advertising/MLB/advertisers/{advertiser_id}/product_ads/ads/search"
        d_str = day.strftime("%Y-%m-%d") if hasattr(day, 'strftime') else str(day)

        for metrics in (self.ADS_METRICS_EXTENDED, self.ADS_METRICS_BASE):
            params = {
                "date_from": d_str, "date_to": d_str,
                "metrics": metrics,
                "limit": 100, "offset": 0
            }
            all_results = []
            failed = False
            while True:
                response = self.request('GET', endpoint, params=params, timeout=30, max_retries=3,
                                        extra_headers={"Api-Version": "2"})
                if not response or response.status_code != 200:
                    failed = True
                    break
                data = response.json()
                results = data.get("results", [])
                all_results.extend(results)
                paging = data.get("paging", {})
                if len(all_results) >= paging.get("total", 0) or not results:
                    break
                params["offset"] += len(results)
                if params["offset"] > 2000:
                    break

            if failed and not all_results:
                # Extended metric set may be unsupported — retry with base set
                continue

            rows = []
            for ad in all_results:
                m = ad.get("metrics", {}) or {}
                rows.append({
                    "item_id": ad.get("item_id"),
                    "cost": float(m.get("cost", 0) or 0),
                    "amount": float(m.get("amount", 0) or 0),
                    "clicks": int(m.get("clicks", 0) or 0),
                    "prints": int(m.get("prints", 0) or 0),
                    "units_quantity": int(m.get("units_quantity", 0) or 0),
                })
            return rows
        return []

    def get_shipping_cost(self, item_id: str, seller_id: str):
        """
        Fetches free shipping cost for the seller.
        """
        try:
            response = self.request('GET', f"/users/{seller_id}/shipping_options/free", params={"item_id": item_id})
            if response.status_code == 200:
                return float(response.json().get("coverage", {}).get("all_country", {}).get("list_cost", 0.0))
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching shipping cost for {item_id}: {e}")
            return 0.0

    def get_shipment(self, shipment_id: str):
        """Fetch shipment details."""
        resp = self.request('GET', f"/shipments/{shipment_id}")
        if resp.status_code == 200: return resp.json()
        return None

    def get_fulfillment_stock(self, inventory_id: str):
        """
        Fetch detailed fulfillment stock, including 'transfer' (incoming) status.
        Endpoint: /inventories/{inventory_id}/stock/fulfillment
        """
        try:
             resp = self.request('GET', f"/inventories/{inventory_id}/stock/fulfillment")
             if resp.status_code == 200:
                 return resp.json()
             elif resp.status_code in [404, 400]:
                 # Inventory ID might be invalid or not Full
                 return None
             else:
                 logger.warning(f"Fulfillment stock fetch failed for {inventory_id}: {resp.status_code}")
                 return None
        except Exception as e:
             logger.error(f"Error fetching fulfillment stock for {inventory_id}: {e}")
             return None

    def update_item_price(self, item_id: str, new_price: float) -> dict:
        """
        Updates the price of an item on Mercado Livre.
        
        Args:
            item_id: The MLB item ID (e.g., 'MLB1234567890')
            new_price: The new price in BRL
            
        Returns:
            dict with 'success': bool, 'old_price': float|None, 'new_price': float, 'error': str|None
        """
        import os
        write_enabled = os.getenv('ML_PRICE_WRITE_ENABLED', 'false').lower() == 'true'
        if not write_enabled:
            return {
                "success": False,
                "status": "locked",
                "error": "PRICE_WRITE_LOCKED",
                "message": "Escrita de preço no Mercado Livre bloqueada por segurança."
            }

        result = {
            "success": False,
            "old_price": None,
            "new_price": new_price,
            "error": None
        }
        
        try:
            # First, get current price for backup
            current_resp = self.request("GET", f"/items/{item_id}")
            if current_resp and current_resp.status_code == 200:
                current_data = current_resp.json()
                result["old_price"] = current_data.get("price")
            
            # Update the price
            update_resp = self.request("PUT", f"/items/{item_id}", json_data={"price": new_price})
            
            if update_resp.status_code == 200:
                result["success"] = True
                logger.info(f"Price updated for {item_id}: {result['old_price']} -> {new_price}")
            else:
                # Parse error for better message
                try:
                    error_data = update_resp.json()
                    causes = error_data.get("cause", [])
                    if causes:
                        cause_msgs = [f"{c.get('code', 'unknown')}: {c.get('message', c.get('type', ''))}" for c in causes]
                        error_msg = f"ML Error: {'; '.join(cause_msgs)}"
                    else:
                        error_msg = error_data.get("message", update_resp.text[:200])
                except:
                    error_msg = f"API returned {update_resp.status_code}: {update_resp.text[:200]}"
                
                result["error"] = error_msg
                logger.error(f"Failed to update price for {item_id}: {error_msg}")
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Exception updating price for {item_id}: {e}")
            
        return result

