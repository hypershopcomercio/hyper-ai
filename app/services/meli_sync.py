
import json
import logging
import requests
import time
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from app.services.meli_auth import MeliAuthService
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.oauth_token import OAuthToken
from app.models.system_log import SystemLog

logger = logging.getLogger(__name__)

class MeliSyncService:
    def __init__(self):
        self.auth = MeliAuthService()
        self.base_url = "https://api.mercadolibre.com"

    def _log(self, db, level, message, details=None, duration=None):
        """Helper to log to SystemLog"""
        try:
            details_str = None
            if details:
                if isinstance(details, dict):
                    details_str = json.dumps(details)
                else:
                    details_str = str(details)

            log = SystemLog(
                module="sync_listings",
                level=level,
                message=message,
                details=details_str,
                duration_ms=duration
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to write log: {e}")

    def sync_listings(self, seller_id=None):
        """
        Syncs all listings for the seller.
        If seller_id is None, tries to find it from token.
        """
        start_time = time.time()
        db = SessionLocal()
        total_synced = 0
        errors = 0
        
        try:
            token = self.auth.get_valid_token()
            if not token:
                raise Exception("No valid token available")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # If no seller_id provided, get from Me
            if not seller_id:
                me_res = requests.get(f"{self.base_url}/users/me", headers=headers)
                me_res.raise_for_status()
                seller_id = me_res.json()["id"]

            logger.info(f"Starting sync for seller {seller_id}")
            print(f"Iniciando sync de listings para seller {seller_id}...") # User requested console.log equivalent
            
            # Scroll Search
            scroll_id = None
            while True:
                url = f"{self.base_url}/users/{seller_id}/items/search?search_type=scan&limit=20"
                if scroll_id:
                    url += f"&scroll_id={scroll_id}"
                
                res = requests.get(url, headers=headers)
                
                # Rate Limit Handling (Basic)
                if res.status_code == 429:
                    logger.warning("Rate limit hit, waiting 5s...")
                    time.sleep(5)
                    continue
                    
                res.raise_for_status()
                data = res.json()
                print(f"URL Chamada: {url}")
                print(f"Items encontrados nesta página: {len(data.get('results', []))}")
                
                results = data.get("results", [])
                if not results:
                    break
                
                # Fetch details for batch
                item_ids = ",".join(results)
                print(f"DEBUG: item_ids len: {len(item_ids)}, content (partial): {item_ids[:50]}...")
                items_res = requests.get(f"{self.base_url}/items?ids={item_ids}", headers=headers)
                
                if items_res.status_code != 200:
                    logger.error(f"Failed to fetch items details: {items_res.status_code} - {items_res.text}")
                    # If batch fails, skip this batch but trying to continue scroll might be risky if scroll_id depends on success? 
                    # Actually scroll_id comes from search, so we can continue.
                    errors += len(results)
                else:
                    items_data = items_res.json()
                    
                    if isinstance(items_data, list):
                        for item_wrapper in items_data:
                            if isinstance(item_wrapper, dict) and item_wrapper.get("code") == 200:
                                item = item_wrapper["body"]
                                self._upsert_ad(db, item)
                                print(f"Item salvo: {item.get('id')} - {item.get('title')}")
                                total_synced += 1
                            else:
                                print(f"Erro item individual: {item_wrapper}")
                                errors += 1
                    else:
                        print(f"CRITICAL: /items returned non-list: {items_data}")
                        errors += len(results)

                scroll_id = data.get("scroll_id")
                if not scroll_id:
                    break
            
            duration = int((time.time() - start_time) * 1000)
            self._log(db, "INFO", "Sync completed", details={"synced": total_synced, "errors": errors}, duration=duration)
            print(f"DEBUG: Sync Loop Finished. Total: {total_synced}, Errors: {errors}")
            return {"success": True, "total": total_synced, "errors": errors}

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self._log(db, "ERROR", "Sync failed", details={"error": str(e)}, duration=duration)
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def sync_single_listing(self, ml_id):
        db = SessionLocal()
        try:
            token = self.auth.get_valid_token()
            if not token:
                raise Exception("No valid token")
            
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/items/{ml_id}", headers=headers)
            res.raise_for_status()
            item = res.json()
            
            ad = self._upsert_ad(db, item)
            self._log(db, "INFO", f"Synced single listing {ml_id}")
            return ad
        except Exception as e:
            self._log(db, "ERROR", f"Failed sync single {ml_id}: {e}")
            raise
        finally:
            db.close()

    def _upsert_ad(self, db, item):
        # Extract fields
        ml_id = item["id"]
        
        # Prepare data dict
        data = {
            "id": ml_id,
            "seller_id": str(item.get("seller_id")), # Ensure capture
            "title": item["title"],
            "price": item["price"],
            "original_price": item.get("original_price"),
            "available_quantity": item["available_quantity"],
            "status": item["status"],
            "listing_type_id": item["listing_type_id"],
            "permalink": item["permalink"],
            "thumbnail": item["thumbnail"],
            "updated_at": datetime.now()
        }
        
        # SKU
        sku = None
        if item.get("seller_custom_field"):
            sku = item["seller_custom_field"]
        else:
            for attr in item.get("attributes", []):
                if attr["id"] == "SELLER_SKU":
                    sku = attr["value_name"]
                    break
        data["sku"] = sku

        # Shipping
        shipping = item.get("shipping", {})
        data["is_full"] = shipping.get("logistic_type") == "fulfillment"
        data["free_shipping"] = shipping.get("free_shipping", False)
        
        # Other
        data["is_catalog"] = item.get("catalog_listing", False)
        
        health = item.get("health", 0.0)
        if isinstance(health, (int, float)):
             data["health_score"] = float(health)
        else:
             data["health_score"] = 0.0

        # Execute Upsert
        stmt = insert(Ad).values(**data)
        
        # Define what to update on conflict
        # We exclude 'id' from set_
        update_dict = {k: v for k, v in data.items() if k != "id"}
        
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"], # Ad.id
            set_=update_dict
        )
        
        db.execute(stmt)
        # Handle Variations
        self._upsert_variations(db, item)
        
        db.commit()
        return data # Return dict as pseudo-object for logging if needed

    def _upsert_variations(self, db, item):
        variations = item.get("variations", [])
        if not variations:
            return

        ad_id = item["id"]
        from app.models.ad_variation import AdVariation
        
        for v in variations:
            v_id = str(v["id"])
            
            # SKU Logic for Variation
            sku = None
            # Check attribute_combinations or seller_custom_field
            # Usually seller_custom_field is the SKU for the variation
            if v.get("seller_custom_field"):
                sku = v.get("seller_custom_field")
            else:
                # Fallback to attributes
                for attr in v.get("attributes", []):
                    if attr["id"] == "SELLER_SKU":
                        sku = attr["value_name"]
                        break
            
            # Prepare Data
            v_data = {
                "id": v_id,
                "ad_id": ad_id,
                "sku": sku,
                "price": v.get("price"),
                "available_quantity": v.get("available_quantity"),
                "attribute_combination": ", ".join([f"{ac['name']}: {ac['value_name']}" for ac in v.get("attribute_combinations", [])])
            }
            
            # Upsert Variation
            stmt = insert(AdVariation).values(**v_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={k: v for k, v in v_data.items() if k != "id"}
            )
            db.execute(stmt)

