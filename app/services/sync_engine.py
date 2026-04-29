
import logging
import datetime
import time 
import concurrent.futures
import sqlalchemy
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService
from app.services.tiny_api import TinyApiService
from app.models.ad import Ad
from app.models.metric import Metric
from app.models.oauth_token import OAuthToken
from app.models.sale import Sale
from app.models.system_config import SystemConfig
from app.models.tiny_product import TinyProduct
from app.models.ad_tiny_link import AdTinyLink
from app.models.ad_variation import AdVariation
from app.models.ad_variation import AdVariation
from app.services.margin_calculator import MarginCalculatorService
from app.models.sync import SyncControl
from app.services.sync_v2.initial_load import InitialLoadService
from app.services.sync_v2.incremental import IncrementalSyncService

logger = logging.getLogger(__name__)

from app.models.ml_visit import MlVisit
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.tiny_stock import TinyStock
from app.models.ml_metrics_daily import MlMetricsDaily

class SyncEngine:
    def __init__(self):
        self.db = SessionLocal()
        self.meli_service = MeliApiService(db_session=self.db)
        self.tiny_service = TinyApiService()
        self.margin_calculator = MarginCalculatorService()
        from app.services.metric_processor import MetricProcessor
        self.metric_processor = MetricProcessor(self.db)
        
        # V2 Services
        self.init_service = InitialLoadService(self.db)
        self.inc_service = IncrementalSyncService(self.db)

    def get_seller_id(self):
        token = self.db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if token and token.user_id:
            return token.user_id
        return settings.MELI_USER_ID

    # Legacy / Mixed Wrapper
    def sync_ads_metrics(self):
        try:
            logger.info("Starting Ads Metrics Sync (Last 30 days)...")
            from app.models.ml_ads_metrics import MlAdsMetric
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=30)
            
            for i in range(31):
                target_date = start_date + datetime.timedelta(days=i)
                should_sync = True
                
                if target_date < end_date - datetime.timedelta(days=3):
                    count = self.db.query(MlAdsMetric).filter(MlAdsMetric.date == target_date).count()
                    if count > 0:
                        should_sync = False
                        
                if not should_sync:
                    continue
                    
                ads_data = self.meli_service.get_ads_performance(None, target_date, target_date)
                
                if ads_data:
                    self.db.query(MlAdsMetric).filter(MlAdsMetric.date == target_date).delete()
                    self.db.commit()
                    
                    for ad_d in ads_data:
                        metric = MlAdsMetric(
                            campaign_id="PADS",
                            date=target_date,
                            cost=ad_d.get("cost", 0),
                            revenue=ad_d.get("amount", 0),
                            clicks=ad_d.get("clicks", 0),
                            impressions=ad_d.get("prints", 0)
                        )
                        self.db.add(metric)
                    self.db.commit()
            logger.info("Ads Metrics Sync Completed!")
        except Exception as e:
            logger.error(f"Ads Metrics Sync Failed: {e}")
            self.db.rollback()

    def sync_orders_incremental(self, lookback_hours: int = None):
        """
        Triggers the V2 Incremental Sync for orders.
        """
        logger.info(f"Triggering V2 Incremental Sync Orders (lookback={lookback_hours})...")
        self.inc_service.sync_orders_incremental(lookback_hours=lookback_hours)

    def check_initial_load(self):
        """
        Triggers V2 Initial Load if not done.
        """
        control = self.db.query(SyncControl).filter(SyncControl.entity == 'orders').first()
        if not control or control.initial_load_status != 'completed':
            logger.info("Starting V2 Initial Load Orders...")
            self.init_service.load_orders()
            
        # Ads
        control_ads = self.db.query(SyncControl).filter(SyncControl.entity == 'ads').first()
        if not control_ads or control_ads.initial_load_status != 'completed':
            logger.info("Starting V2 Initial Load Ads...")
            self.init_service.load_ads()

    def _log_sync(self, log_type: str, status: str, processed=0, success=0, error=0, msg=None, details=None, start_time=None):
        try:
            duration = None
            if start_time:
                duration = int((datetime.datetime.now() - start_time).total_seconds() * 1000)
                
            level = "ERROR" if status == "error" else "INFO"
            
            import json
            detail_data = {
                "processed": processed,
                "success": success,
                "error_count": error,
                "raw_details": details
            }
            
            sql = "INSERT INTO system_logs (module, level, message, details, duration_ms, status, timestamp) VALUES (:module, :level, :message, :details, :duration, :status, NOW())"
            
            params = {
                "module": log_type,
                "level": level,
                "message": msg or f"Sync {status}",
                "details": json.dumps(detail_data),
                "duration": duration,
                "status": status
            }
            
            self.db.execute(sqlalchemy.text(sql), params)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
            self.db.rollback()

    def sync_ads(self):
        logger.info("Starting Ads Sync...")
        start_time = datetime.datetime.now()
        self._log_sync("listings", "running", start_time=start_time)

        processed_count = 0
        success_count = 0
        error_count = 0
        
        try:
            seller_id = self.get_seller_id()
            if not seller_id:
                raise Exception("No Seller ID found.")

            item_ids = self.meli_service.get_user_items(seller_id)
            total_items = len(item_ids)
            logger.info(f"Found {total_items} active items.")
            
            chunk_size = 50
            for i in range(0, total_items, chunk_size):
                chunk = item_ids[i:i+chunk_size]
                try:
                    items_details = self.meli_service.get_item_details(chunk)
                    for item in items_details:
                        try:
                            self._upsert_ad(item, seller_id)
                            success_count += 1
                        except Exception as e_item:
                            logger.error(f"Failed to process ad {item.get('id')}: {e_item}")
                            error_count += 1
                        processed_count += 1
                    self.db.commit() 
                except Exception as e_chunk:
                    logger.error(f"Chunk failed: {e_chunk}")
                    error_count += len(chunk)

            logger.info("Ads Sync completed.")
            self._log_sync("listings", "success", processed_count, success_count, error_count, start_time=start_time)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ads Sync failed: {e}")
            self._log_sync("listings", "error", processed_count, success_count, error_count, str(e), start_time=start_time)

    def _upsert_ad(self, item_data: dict, seller_id: str):
        ad_id = item_data["id"]
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            ad = Ad(id=ad_id)
            self.db.add(ad)
        
        ad.seller_id = seller_id
        ad.title = item_data.get("title")[:500]
        ad.category_name = item_data.get("category_id") 
        ad.permalink = item_data.get("permalink")
        ad.thumbnail = item_data.get("thumbnail")
        ad.pictures = item_data.get("pictures") 
        ad.attributes = item_data.get("attributes") 
        ad.attributes = item_data.get("attributes") 
        ad.video_id = item_data.get("video_id")
        ad.short_description = item_data.get("short_description", {}).get("content") if isinstance(item_data.get("short_description"), dict) else item_data.get("short_description")
        # Hyper Sync 2.0: Promotion Logic Removed (Reverted)
        
        # Original simple mapping
        ad.price = float(item_data.get("price", 0))
        ad.original_price = float(item_data.get("original_price")) if item_data.get("original_price") else None
             
        ad.currency_id = item_data.get("currency_id")
        ad.available_quantity = int(item_data.get("available_quantity", 0))
        ad.sold_quantity = int(item_data.get("sold_quantity", 0))
        ad.status = item_data.get("status")
        ad.listing_type_id = item_data.get("listing_type_id")
        ad.listing_type = item_data.get("listing_type_id") 
        shipping = item_data.get("shipping", {})
        ad.free_shipping = shipping.get("free_shipping", False)
        ad.shipping_mode = shipping.get("mode") 
        ad.is_full = (shipping.get("logistic_type") == "fulfillment")
        ad.health = float(item_data.get("health", 0)) if item_data.get("health") else 0.0

        sku = None
        gtin = None
        for attr in item_data.get("attributes", []):
            aid = attr.get("id")
            val = attr.get("value_name")
            if aid == "SELLER_SKU":
                sku = val.strip() if val else None
            elif aid == "GTIN":
                gtin = val.strip() if val else None
        
        ad.sku = sku
        ad.gtin = gtin
        
        # ad.shipping_cost = 0.0
        # if ad.free_shipping:
        #      ad.shipping_cost = self.meli_service.get_shipping_cost(ad.id, seller_id)
        
        # if ad.is_full:
        #     inventory_id = item_data.get("inventory_id")
        #     if inventory_id:
        #         f_data = self.meli_service.get_fulfillment_stock(inventory_id)
        #         if f_data:
        #             # Parse 'transfer' quantity
        #             # "not_available_detail": [{"status": "transfer", "quantity": 135}, ...]
        #             details = f_data.get("not_available_detail", [])
        #             transfer_qty = 0
        #             for d in details:
        #                 if d.get("status") == "transfer":
        #                     transfer_qty += d.get("quantity", 0)
        #             
        #             ad.stock_incoming = transfer_qty
        
        # Sync Costs & Margins (Tiny + Tax + Fixed)
        try:
            # 1. Get Configs
            from app.services.tax_service import TaxService
            from app.models.system_config import SystemConfig
            
            # Tax Rate
            sc_tax = self.db.query(SystemConfig).filter(SystemConfig.key == 'aliquota_simples').first()
            if sc_tax:
                tax_rate = float(sc_tax.value)
            else:
                # Fallback to default or calculate if completely missing
                # To obtain an instance of TaxService, we need to handle its init or use static methods if available
                # But TaxService.__init__ takes db.
                ts = TaxService(self.db)
                tax_rate = ts.update_system_tax_rate()
            
            # Fixed Cost
            sc_fixed = self.db.query(SystemConfig).filter(SystemConfig.key == 'custo_fixo_pedido').first()
            fixed_cost = float(sc_fixed.value) if sc_fixed else 0.0
            
            # Inbound Cost (Full Only)
            inbound_cost = 0.0
            if ad.is_full:
                sc_inbound = self.db.query(SystemConfig).filter(SystemConfig.key == 'avg_inbound_cost').first()
                inbound_cost = float(sc_inbound.value) if sc_inbound else 0.0
            
            # 2. Process Cost & Margin (Links Tiny, updates cost, tax, margin)
            # This method handles SKU resolution, Tiny linking, Cost update, and Margin Calc
            self._process_ad_cost(ad, tax_rate, fixed_cost, inbound_cost)
            
        except Exception as e:
            logger.error(f"Error processing costs for ad {ad.id}: {e}")
            # Fallback for tax to ensure it's not null if process fails
            if ad.tax_cost is None and ad.price:
                ad.tax_cost = 0.0

        ad.last_updated = datetime.datetime.now()
        ad.updated_at = datetime.datetime.now()
        
        if "variations" in item_data and item_data["variations"]:
             self._upsert_variations(ad.id, item_data["variations"])

    def _upsert_variations(self, ad_id: str, variations_data: list):
        for var_data in variations_data:
            var_id = str(var_data.get("id"))
            variation = self.db.query(AdVariation).filter(AdVariation.id == var_id).first()
            if not variation:
                variation = AdVariation(id=var_id, ad_id=ad_id)
                self.db.add(variation)
            
            var_sku = None
            if "attributes" in var_data:
                for attr in var_data.get("attributes", []):
                    if attr.get("id") == "SELLER_SKU":
                         val = attr.get("value_name")
                         var_sku = val.strip() if val else None
                         break
            variation.sku = var_sku
            variation.price = float(var_data.get("price", 0))
            variation.available_quantity = int(var_data.get("available_quantity", 0))
            variation.sold_quantity = int(var_data.get("sold_quantity", 0))
            
            comb = []
            if "attribute_combinations" in var_data:
                 for comb_attr in var_data["attribute_combinations"]:
                      comb.append(f"{comb_attr.get('name')}: {comb_attr.get('value_name')}")
            variation.attribute_combination = ", ".join(comb)

    def _fetch_visits_wrapper(self, ad_id):
        try:
             return self.meli_service.get_visits_time_window(ad_id, last=120, unit="day")
        except Exception as e:
             logger.error(f"Thread fetch failed for {ad_id}: {e}")
             return None

    def sync_visits(self):
        logger.info("Starting Visits Sync...")
        start_time = datetime.datetime.now()
        processed = 0
        success = 0
        error = 0
        
        try:
            seller_id = self.get_seller_id()
            ads = self.db.query(Ad).filter(Ad.status == 'active').all() 
            total = len(ads)
            logger.info(f"Syncing visits for {total} active ads (Parallel).")
            
            self.meli_service.get_headers() 
            ad_map = {ad.id: ad for ad in ads}
            ad_ids = list(ad_map.keys())
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_to_id = {executor.submit(self._fetch_visits_wrapper, aid): aid for aid in ad_ids}
                
                for future in concurrent.futures.as_completed(future_to_id):
                    aid = future_to_id[future]
                    ad = ad_map[aid]
                    processed += 1
                    
                    try:
                        data = future.result()
                        if data and "results" in data:
                            for day_data in data["results"]:
                                v_date_str = day_data.get("date")[:10] 
                                v_count = day_data.get("visits", 0)
                                v_date = datetime.datetime.strptime(v_date_str, "%Y-%m-%d").date()
                                
                                visit_rec = self.db.query(MlVisit).filter(MlVisit.item_id == aid, MlVisit.date == v_date).first()
                                if not visit_rec:
                                    visit_rec = MlVisit(item_id=aid, date=v_date)
                                    self.db.add(visit_rec)
                                visit_rec.visits = day_data.get("total", 0)
                                
                                # Explicit Upsert for Metrics Daily
                                existing_metric = self.db.query(MlMetricsDaily).filter(
                                    MlMetricsDaily.item_id == aid, 
                                    MlMetricsDaily.date == v_date
                                ).first()
                                
                                if existing_metric:
                                    existing_metric.visits = day_data.get("total", 0)
                                else:
                                    new_metric = MlMetricsDaily(item_id=aid, date=v_date, visits=day_data.get("total", 0))
                                    self.db.add(new_metric)
                                    # self.db.flush() # Optional, but commit handles it
                                
                            # Sum all visits from the time window (up to 120 days)
                            # ML API max is 120 days, so this is the best we can get
                            total_visits_period = sum(d.get('total', 0) for d in data['results'])
                            ad.visits_30d = total_visits_period  # Actually represents 120d now
                            ad.total_visits = total_visits_period  # Keep consistent with UI
                            
                            ad.visits_last_updated = datetime.datetime.now()
                            success += 1
                        else:
                            if data is None: error += 1
                    except Exception as e_process:
                        logger.error(f"Processing result failed for {aid}: {e_process}")
                        error += 1
                    if processed % 50 == 0:
                        self.db.commit()
            
            self.db.commit()
            self._log_sync("visits", "success", processed, success, error, start_time=start_time)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Visits Sync Failed: {e}")
            self._log_sync("visits", "error", processed, success, error, str(e), start_time=start_time)

    def sync_orders(self):
        """
        [DEPRECATED Logic] Now redirects to V2 Incremental Sync.
        Syncs recent orders, populates ml_orders, and metrics.
        """
        logger.info("Starting Orders Sync (Redirecting to V2 Incremental with 48h lookback)...")
        # For legacy 'Sync All' button reliability, we force 48h lookback
        self.sync_orders_incremental(lookback_hours=48)
        
        # Update Metrics Processing Trigger
        # Currently done in run_daily_sync or sync_metrics wrapper. 
        # But sync_orders is called BY sync_metrics usually.
        # So we just do the sync here. The processing happens in sync_metrics step 3.
        pass
    def _process_order_full(self, order_data: dict):
        ml_order_id = str(order_data["id"])
        
        # Upsert MlOrder
        order = self.db.query(MlOrder).filter(MlOrder.ml_order_id == ml_order_id).first()
        if not order:
            order = MlOrder(ml_order_id=ml_order_id)
            self.db.add(order)
        
        order.seller_id = str(order_data.get("seller", {}).get("id"))
        order.status = order_data.get("status")
        
        # Date Parsing with UTC Conversion
        dt_str = order_data["date_created"]
        if dt_str.endswith('Z'):
             dt_str = dt_str.replace('Z', '+00:00')
        dt_obj = datetime.datetime.fromisoformat(dt_str)
        if dt_obj.tzinfo:
             dt_obj = dt_obj.astimezone(datetime.timezone.utc)
        order.date_created = dt_obj.replace(tzinfo=None)
        
        order.total_amount = float(order_data.get("total_amount", 0))
        order.currency_id = order_data.get("currency_id")
        order.buyer_id = str(order_data.get("buyer", {}).get("id"))
        
        # Tags Mapping
        tags_list = order_data.get("tags", [])
        import json
        order.tags = json.dumps(tags_list) 
        order.status_detail = str(order_data.get("status_detail"))

        shipping = order_data.get("shipping", {})
        order.shipping_id = str(shipping.get("id")) if shipping.get("id") else None
        # Shipping Cost logic (To be refined)
        order.shipping_cost = 0.0 # Placeholder
        
        # Order Items
        items_data = order_data.get("order_items", [])
        for item_d in items_data:
            ml_item_id = item_d.get("item", {}).get("id")
            
            # Helper to check item uniqueness in order (composite key approach simulation)
            # Or just filter by order_id + item_id if unique enough.
            db_item = self.db.query(MlOrderItem).filter(MlOrderItem.ml_order_id == ml_order_id, MlOrderItem.ml_item_id == ml_item_id).first()
            if not db_item:
                db_item = MlOrderItem(ml_order_id=ml_order_id, ml_item_id=ml_item_id)
                self.db.add(db_item)
            
            db_item.sku = item_d.get("item", {}).get("seller_sku")
            db_item.title = item_d.get("item", {}).get("title")
            db_item.quantity = int(item_d.get("quantity", 1))
            db_item.unit_price = float(item_d.get("unit_price", 0))
            db_item.sale_fee = float(item_d.get("sale_fee", 0))

            # Update Metric (Daily Sales)
            # Use order.date_created
            sale_date = order.date_created.date()
            metric_rec = self.db.query(MlMetricsDaily).filter(MlMetricsDaily.item_id == ml_item_id, MlMetricsDaily.date == sale_date).first()
            if not metric_rec:
                metric_rec = MlMetricsDaily(item_id=ml_item_id, date=sale_date)
                self.db.add(metric_rec)
            
            # Logic: We might over-count if we re-process same order multiple times.
            # Ideally, capture snapshot or difference?
            # Or always recalculate daily stats from orders table?
            # Recalculating is safer but slower. 
            # For now, let's just ensure we don't double count if we just re-run safe upsert.
            # Actually, `metric_rec` fields like visits are accumulative/absolute from API.
            # Sales qty should be sum of orders for that day.
            # Hack: We won't increment here. We will run a separate aggregation query or just trust the daily sum.
            pass

    def sync_tiny_stock(self):
        """Syncs stock from Tiny for all linked products."""
        logger.info("Starting Tiny Stock Sync...")
        start_time = datetime.datetime.now()
        
        self._log_sync("stock", "running", start_time=start_time)

        processed = 0
        success = 0
        error = 0
        
        try:
            # Iterate over TinyProducts (or AdTinyLinks)
            # Better to iterate AdTinyLinks to focus on relevant SKUs
            links = self.db.query(AdTinyLink).all()
            total = len(links)
            logger.info(f"Checking stock for {total} linked products.")
            
            for link in links:
                processed += 1
                try:
                    tiny_prod = self.db.query(TinyProduct).filter(TinyProduct.id == link.tiny_product_id).first()
                    if not tiny_prod or not tiny_prod.sku:
                        continue
                        
                    sku = tiny_prod.sku
                    
                    # 1. Sync Stock
                    stock_data = self.tiny_service.get_stock(sku)
                    
                    if stock_data:
                        # stock_data is dict: {id, nome, codigo, saldo, ...}
                        # "saldo" is the quantity
                        qty = int(stock_data.get("saldo", 0))
                        
                        # Upsert TinyStock
                        ts = self.db.query(TinyStock).filter(TinyStock.sku == sku).first()
                        if not ts:
                            ts = TinyStock(sku=sku)
                            self.db.add(ts)
                        ts.quantity = qty
                        ts.last_updated = datetime.datetime.now()
                        
                        # Update Ad Divergence
                        ad = self.db.query(Ad).filter(Ad.id == link.ad_id).first()
                        if ad:
                            ad.stock_tiny = qty
                            ad.stock_divergence = ad.available_quantity - qty
                    
                    # 2. Sync Cost (Enhanced to fix stale cost issue)
                    # We use the ID to fetching details which includes 'preco_custo'
                    if tiny_prod.id:
                        details = self.tiny_service.get_product_details(str(tiny_prod.id))
                        if details:
                             # Update Cost
                             new_cost = float(details.get("preco_custo", 0.0))
                             tiny_prod.cost = new_cost
                             tiny_prod.name = details.get("nome", tiny_prod.name) # Update name too
                             tiny_prod.last_updated = datetime.datetime.now()
                             
                             # Update Ad Cost immediately if linked
                             ad = self.db.query(Ad).filter(Ad.id == link.ad_id).first()
                             if ad:
                                 ad.cost = new_cost
                                 # ad.last_updated = datetime.datetime.now() # Don't update ad timestamp to avoid trigger loop?
                                 
                    success += 1
                except Exception as e_stock:
                    logger.error(f"Stock/Cost Sync failed for link {link.id}: {e_stock}")
                    error += 1
            
            self.db.commit()
            self._log_sync("stock", "success", processed, success, error, start_time=start_time)
            
            # Also sync variation costs from order items
            logger.info("Triggering Variation Costs Sync after Stock Sync...")
            self.sync_variation_costs()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Stock Sync Failed: {e}")
            self._log_sync("stock", "error", processed, success, error, str(e), start_time=start_time)

    def _update_visits_metric(self, ad: Ad):
        # Meli API for visits
        # visits = self.meli_service.get_visits(ad.id) 
        # visits_window = visits['last_30_days']...
        # For simplicity, we assume meli_service has this or we skip if not implemented yet.
        # The prompt didn't ask for visits fix, but it's part of the file.
        # Assuming MeliApiService has get_total_visits or similar.
        # In previous code logic, we used snapshots.
        # Let's verify MeliApiService if I can.
        # I'll assumme existing field in Ad is enough or we fetch item again?
        # Item details endpoint (used in sync_ads) generally does NOT return total_visits.
        # A separate call items/{id}/visits is needed.
        pass

    def _process_ad_cost(self, ad: Ad, tax_rate: float, fixed_cost: float, inbound_cost: float = 0.0):
        # 1. Resolve SKU
        sku = ad.sku.strip() if ad.sku else None
        # If no SKU on ad, try variation (pick first or logic?)
        if not sku:
            # Import strictly inside method to avoid circular imports if any, though not expected here
            from app.models.ad_variation import AdVariation
            var = self.db.query(AdVariation).filter(AdVariation.ad_id == ad.id).first()
            if var and var.sku:
                sku = var.sku.strip()
        
        tiny_prod = None
        
        # 1. Check Link (Manual or Previous Auto-Link) - Check this regardless of SKU presence
        link = self.db.query(AdTinyLink).filter(AdTinyLink.ad_id == ad.id).first()
        if link:
            tiny_prod = self.db.query(TinyProduct).filter(TinyProduct.id == link.tiny_product_id).first()
            if not tiny_prod:
                # Orphan link detected (linked product no longer exists)
                logger.warning(f"Orphan AdTinyLink found for Ad {ad.id}. removing link.")
                self.db.delete(link)
                self.db.flush()
        
        # 2. If no link, try to find via SKU/GTIN
        if not tiny_prod and sku:
             # Search locally first
             tiny_prod = self.db.query(TinyProduct).filter(TinyProduct.sku == sku).first()
             
             # If local search failed, Try GTIN local search
             if not tiny_prod and ad.gtin:
                  tiny_prod = self.db.query(TinyProduct).filter(TinyProduct.sku == ad.gtin).first()

             # If still not found, Sync from Tiny API
             if not tiny_prod:
                 # Try SKU
                 logger.info(f"Syncing from Tiny API for SKU: {sku}")
                 tiny_prod = self._fetch_and_save_tiny(sku)
                 
                 # Fallback: Try GTIN if SKU failed
                 if not tiny_prod and ad.gtin:
                     logger.info(f"Syncing from Tiny API for GTIN: {ad.gtin}")
                     tiny_prod = self._fetch_and_save_tiny(ad.gtin)
             
             if tiny_prod:
                 # Create Link
                 try:
                     with self.db.begin_nested():
                         # Double-check link didn't appear concurrently
                         existing_link = self.db.query(AdTinyLink).filter(AdTinyLink.ad_id == ad.id).first()
                         if not existing_link:
                             new_link = AdTinyLink(ad_id=ad.id, tiny_product_id=tiny_prod.id)
                             self.db.add(new_link)
                             self.db.flush() 
                             logger.info(f"Linked Ad {ad.id} to TinyProduct {tiny_prod.id}")
                 except Exception as e:
                     logger.error(f"Failed to link Ad {ad.id} to TinyProduct {tiny_prod.id}: {e}")


        
        # Update Ad Cost from TinyProduct
        if tiny_prod and tiny_prod.cost is not None:
             ad.cost = tiny_prod.cost

        # Calculate Margin
        self.margin_calculator.calculate_margin(ad, tiny_prod, tax_rate, fixed_cost, inbound_cost)

    def _fetch_and_save_tiny(self, sku: str):
        # Fetch from API
        p_data = self.tiny_service.search_product(sku)
        if p_data:
            tiny_id = p_data.get("id")
            if not tiny_id:
                return None
            
            # Fetch FULL details to get parent/variations
            details = self.tiny_service.get_product_details(str(tiny_id))
            if not details:
                # Fallback to search data
                details = p_data
            
            # Check for Parent
            parent_id = details.get("id_produto_pai")
            if parent_id and str(parent_id) != "0" and str(parent_id) != str(tiny_id):
                # Fetch Parent to get all siblings
                logger.info(f"SKU {sku} has parent {parent_id}. Fetching parent & siblings...")
                parent_details = self.tiny_service.get_product_details(str(parent_id))
                if parent_details:
                    # Save Parent
                    self._save_tiny_product_from_data(parent_details)
                    # Save All Variations (Siblings)
                    if "variacoes" in parent_details:
                        self._process_variations_list(parent_details["variacoes"])
                    
                    # Refetch self from DB to return correct object
                    return self.db.query(TinyProduct).filter(TinyProduct.id == tiny_id).first()

            # If no parent or parent fetch failed, save self
            tp = self._save_tiny_product_from_data(details)
            
            # If self has variations (is parent)
            if "variacoes" in details:
                self._process_variations_list(details["variacoes"])
                
            return tp
        return None

    def _save_tiny_product_from_data(self, data: dict):
        t_id = str(data.get("id"))
        tp = self.db.query(TinyProduct).filter(TinyProduct.id == t_id).first()
        if not tp:
            tp = TinyProduct(id=t_id)
            self.db.add(tp)
        
        tp.sku = data.get("codigo")
        tp.name = data.get("nome")
        tp.cost = float(data.get("preco_custo", 0))
        self.db.flush()
        return tp

    def _process_variations_list(self, variations: list):
        """
        Process list of variations from Tiny API details.
        Format: [{'variacao': {'id':..., 'codigo':..., ...}}, ...]
        """
        for v_wrapper in variations:
            v_data = v_wrapper.get("variacao")
            if v_data:
                self._save_tiny_product_from_data(v_data) 
        
    def sync_metrics(self):
        """
        Runs the processing: 
        1. Sync Visits from ML.
        2. Sync Orders from ML.
        3. Process Trends & Aggregations (MetricProcessor).
        4. Recalculate Margins (MarginCalculator).
        """
        logger.info("Starting Metrics & Margin Processing...")
        try:
            # 1. Sync Visits
            self._log_sync("visits", "running", start_time=datetime.datetime.now())
            self.sync_visits()

            # 2. Sync Orders
            self._log_sync("orders", "running", start_time=datetime.datetime.now())
            self.sync_orders()

            # 3. Process Trends & Aggregations
            self._log_sync("metrics_processing", "running", start_time=datetime.datetime.now())
            
            # Aggregate Sales First (Orders -> Ads)
            self.metric_processor.aggregate_sales_metrics()
            # Aggregate Daily Sales (Orders -> Daily Metrics)
            self.metric_processor.aggregate_daily_sales()

            # Calculate Trends (7d changes)
            self.metric_processor.process_all()
            
            self._log_sync("metrics_processing", "success", start_time=datetime.datetime.now()) # End log

        except Exception as e:
            self.db.rollback()
            logger.error(f"Metrics Processing failed: {e}")
            self._log_sync("metrics_processing", "error", msg=str(e), start_time=datetime.datetime.now())

        # 4. Process Margins (Now Cleanly Separated)
        self.sync_margins()

    def sync_margins(self):
        """
        Recalculates margins and taxes for all active ads.
        Indepedent step to ensure tax updates even if metrics fail.
        """
        logger.info("Starting Margin Processing...")
        start_time = datetime.datetime.now()
        try:
            from app.services.tax_service import TaxService
            tax_service = TaxService(db_session=self.db)
            
            # Update System Tax Rate based on RBT12
            tax_service.update_system_tax_rate()
            
            seller_id = self.get_seller_id()
            # Calculate for ALL ads (Active + Paused) to prevent confusion
            ads = self.db.query(Ad).all()
            
            # Fetch Configurations
            tax_config = self.db.query(SystemConfig).filter(
                and_(SystemConfig.group == 'geral', SystemConfig.key == "aliquota_simples")
            ).first()
            
            # Fallback to 12.5 if not found
            tax_rate = float(tax_config.value) if tax_config and tax_config.value else 12.5
            
            fixed_pkg_config = self.db.query(SystemConfig).filter(SystemConfig.key == "fixed_packaging_cost").first()
            fixed_pkg = float(fixed_pkg_config.value) if fixed_pkg_config and fixed_pkg_config.value else 0.0
            
            total = len(ads)
            logger.info(f"Recalculating margins for {total} active ads (Tax: {tax_rate}%, Fixed: {fixed_pkg})...")
            
            idx = 0
            for ad in ads:
                try:
                    self._process_ad_cost(ad, tax_rate, fixed_pkg)
                    idx += 1
                except Exception as e_ad:
                    logger.error(f"Ad {ad.id} calc failed: {e_ad}")
                
                if idx % 100 == 0:
                    self.db.commit()
            
            self.db.commit()
            logger.info("Margin Processing completed.")
            self._log_sync("margins", "success", processed=total, success=idx, start_time=start_time)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Margin Processing failed: {e}")
            self._log_sync("margins", "error", msg=str(e), start_time=start_time)

    def sync_ads_spend(self):
        pass

    def sync_variation_costs(self):
        """
        Sync costs for all unique SKUs from order items.
        For each SKU not already in TinyProduct (or with cost=0), 
        fetches from Tiny API and saves to database.
        Called by sync_tiny_stock and general sync.
        """
        logger.info("Starting Variation Costs Sync...")
        self._log_sync("variation_costs", "running", start_time=datetime.datetime.now())
        
        try:
            from sqlalchemy import distinct
            from app.models.ml_order import MlOrderItem
            
            # Get all unique SKUs from order items
            all_skus = self.db.query(distinct(MlOrderItem.sku)).filter(MlOrderItem.sku != None).all()
            all_skus = [sku[0] for sku in all_skus if sku[0]]
            
            logger.info(f"Found {len(all_skus)} unique SKUs in order items")
            
            synced = 0
            skipped = 0
            errors = 0
            
            for sku in all_skus:
                # Check if already exists with cost
                existing = self.db.query(TinyProduct).filter(TinyProduct.sku == sku).first()
                if existing and existing.cost and existing.cost > 0:
                    skipped += 1
                    continue
                
                # Fetch from Tiny API
                try:
                    p_data = self.tiny_service.search_product(sku)
                    if p_data and p_data.get("id"):
                        cost = float(p_data.get("preco_custo", 0) or 0)
                        
                        if existing:
                            existing.cost = cost
                            existing.name = p_data.get("nome", existing.name)
                        else:
                            new_tp = TinyProduct(
                                id=str(p_data.get("id")),
                                sku=p_data.get("codigo"),
                                name=p_data.get("nome"),
                                cost=cost
                            )
                            self.db.add(new_tp)
                        
                        synced += 1
                        
                        # Commit every 50 to avoid large transactions
                        if synced % 50 == 0:
                            self.db.commit()
                    else:
                        errors += 1
                except Exception as e:
                    logger.warning(f"Error syncing SKU {sku}: {e}")
                    errors += 1
            
            self.db.commit()
            logger.info(f"Variation Costs Sync complete: {synced} synced, {skipped} skipped, {errors} errors")
            self._log_sync("variation_costs", "success", start_time=datetime.datetime.now())
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Variation Costs Sync failed: {e}")
            self._log_sync("variation_costs", "error", msg=str(e), start_time=datetime.datetime.now())
