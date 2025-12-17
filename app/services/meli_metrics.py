
import logging
import requests
import time
from datetime import datetime, timedelta, date
from sqlalchemy.dialects.postgresql import insert
from app.services.meli_auth import MeliAuthService
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.metric import Metric
from app.models.oauth_token import OAuthToken
from app.models.system_log import SystemLog

logger = logging.getLogger(__name__)

class MeliMetricsService:
    def __init__(self):
        self.auth = MeliAuthService()
        self.base_url = "https://api.mercadolibre.com"

    def _log(self, db, level, message, details=None):
        try:
            log = SystemLog(module="sync_metrics", level=level, message=message, details=str(details))
            db.add(log)
            db.commit()
        except:
            pass

    def get_headers(self):
        token = self.auth.get_valid_token()
        if not token:
            raise Exception("No valid token")
        return {"Authorization": f"Bearer {token}"}

    def sync_visits(self, target_date=None):
        """Syncs visits for all active listings for a specific date (default today)"""
        if not target_date:
            target_date = date.today()
        
        db = SessionLocal()
        count = 0
        try:
            # Get active listings
            ads = db.query(Ad).filter(Ad.status == 'active').all()
            headers = self.get_headers()
            
            date_str = target_date.strftime("%Y-%m-%d")
            
            for ad in ads:
                try:
                    url = f"{self.base_url}/items/{ad.id}/visits?date_from={date_str}&date_to={date_str}"
                    res = requests.get(url, headers=headers)
                    if res.status_code == 429:
                        time.sleep(1) # Simple backoff
                        res = requests.get(url, headers=headers)
                        
                    if res.status_code == 200:
                        data = res.json()
                        # data structure: { item_id, date_from, date_to, total_visits, visits_detail: [...] }
                        visits = data.get("total_visits", 0)
                        
                        # Upsert Metric
                        self._upsert_metric(db, ad.id, target_date, visits=visits)
                        count += 1
                        
                    time.sleep(0.05) # Rate limit protection (20 req/s roughly)
                except Exception as e:
                    logger.warning(f"Failed visits for {ad.id}: {e}")
            
            self._log(db, "INFO", f"Synced visits for {count} ads on {date_str}")
            return count
        except Exception as e:
            self._log(db, "ERROR", f"Sync visits failed: {e}")
            raise
        finally:
            db.close()

    def sync_orders(self, target_date=None):
        """Syncs sales quantity and revenue from orders"""
        if not target_date:
            target_date = date.today()
            
        db = SessionLocal()
        try:
            headers = self.get_headers()
            
            # Get seller ID
            # Assuming we got it via auth or lookup
            token_rec = db.query(OAuthToken).filter_by(provider="mercadolivre").first()
            seller_id = token_rec.seller_id or token_rec.user_id
            
            date_from = f"{target_date.strftime('%Y-%m-%d')}T00:00:00.000-03:00"
            date_to = f"{target_date.strftime('%Y-%m-%d')}T23:59:59.999-03:00"
            
            # Helper to fetch all orders pages
            all_orders = []
            offset = 0
            limit = 50
            while True:
                url = f"{self.base_url}/orders/search?seller={seller_id}&order.date_created.from={date_from}&order.date_created.to={date_to}&offset={offset}&limit={limit}&sort=date_desc"
                res = requests.get(url, headers=headers)
                if res.status_code == 429:
                     time.sleep(2)
                     continue
                res.raise_for_status()
                data = res.json()
                results = data.get("results", [])
                if not results:
                    break
                
                all_orders.extend(results)
                offset += limit
                total = data.get("paging", {}).get("total", 0)
                if offset >= total:
                    break
            
            # Process orders
            sales_map = {} # item_id -> { qty, revenue }
            
            for order in all_orders:
                # Filter strictly paid? User req: "status='paid'"
                if order.get("status") != "paid":
                    continue
                
                for item in order.get("order_items", []):
                    item_id = item.get("item", {}).get("id")
                    qty = item.get("quantity", 0)
                    price = item.get("unit_price", 0)
                    
                    if item_id:
                        if item_id not in sales_map:
                            sales_map[item_id] = {"qty": 0, "rev": 0.0}
                        sales_map[item_id]["qty"] += qty
                        sales_map[item_id]["rev"] += (price * qty)
            
            # Upsert sales
            updated = 0
            for item_id, stats in sales_map.items():
                self._upsert_metric(db, item_id, target_date, sales=stats["qty"], revenue=stats["rev"])
                updated += 1
                
            self._log(db, "INFO", f"Synced orders for {target_date}, updated {updated} items")
            return updated
            
        except Exception as e:
            self._log(db, "ERROR", f"Sync orders failed: {e}")
            raise
        finally:
            db.close()

    def sync_metrics(self, target_date=None):
        if not target_date:
            target_date = date.today()
        
        visits = self.sync_visits(target_date)
        orders = self.sync_orders(target_date)
        return {"date": str(target_date), "visits_updated": visits, "orders_updated": orders}

    def sync_metrics_range(self, start_date_str, end_date_str):
        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        current = start
        results = []
        while current <= end:
            res = self.sync_metrics(current)
            results.append(res)
            current += timedelta(days=1)
            time.sleep(0.5) # Delay between days
            
        return results

    def _upsert_metric(self, db, ad_id, date_obj, visits=None, sales=None, revenue=None, conversion=None):
        from sqlalchemy.dialects.postgresql import insert
        
        # Prepare data
        data = {
            "ad_id": ad_id,
            "date": date_obj
        }
        
        # We only set values if they are provided, but upsert requires a full set for the insert part usually.
        # Logic: If row doesn't exist, we insert with provided values + defaults.
        # If exists, we update provided values.
        
        if visits is not None: data["visits"] = visits
        else: data["visits"] = 0 # Default for insert
            
        if sales is not None: data["sales"] = sales
        else: data["sales"] = 0
            
        if revenue is not None: data["gross_revenue"] = revenue
        else: data["gross_revenue"] = 0.0
            
        if conversion is not None: data["conversion_rate"] = conversion
        else: data["conversion_rate"] = 0.0
            
        stmt = insert(Metric).values(**data)
        
        # Update part: only update fields that are not None in the arguments
        # Actually arguments passed might be None if we are just syncing visits.
        # So we should only update 'visits' if visits is not None.
        # Since I constructed 'data' with defaults for insert, I need separate dict for update.
        
        update_dict = {}
        if visits is not None: update_dict["visits"] = visits
        if sales is not None: update_dict["sales"] = sales
        if revenue is not None: update_dict["gross_revenue"] = revenue
        if conversion is not None: update_dict["conversion_rate"] = conversion
        
        if not update_dict:
            return # Nothing to update
            
        stmt = stmt.on_conflict_do_update(
            constraint='uq_ad_date', # Named constraint in model
            set_=update_dict
        )
        
        try:
            db.execute(stmt)
            db.commit()
        except Exception as e:
            # If constraint name issue, try index_elements
            # Fallback not needed if model matches DB.
            logger.error(f"Metric upsert failed: {e}")
            raise
