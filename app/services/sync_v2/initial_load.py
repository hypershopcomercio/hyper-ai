import logging
import time
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.sync import SyncControl, SyncJob
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.ad import Ad
from app.models.ad_variation import AdVariation
from app.services.meli_api import MeliApiService

logger = logging.getLogger(__name__)

# Constants
BATCH_SIZE = 50

class InitialLoadService:
    def __init__(self, db: Session):
        self.db = db
        self.ml_api = MeliApiService(db)
        
    def _get_seller_id(self):
        from app.models.oauth_token import OAuthToken
        token = self.db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        return token.user_id if token else None

    # -------------------------------------------------------------------------
    # ORDERS
    # -------------------------------------------------------------------------
    def load_orders(self):
        ENTITY = 'orders'
        seller_id = self._get_seller_id()
        if not seller_id:
            logger.error("No seller_id found for sync.")
            return

        control = self.db.query(SyncControl).filter(SyncControl.entity == ENTITY).first()
        if not control:
            control = SyncControl(entity=ENTITY)
            self.db.add(control)
            self.db.commit()
            
        if control.initial_load_status == 'running':
            # Check if stale (> 1h)
            if control.updated_at and (datetime.now(timezone.utc) - control.updated_at).seconds > 3600:
                logger.warning("Resuming stale job...")
            else:
                logger.warning("Initial load already running for orders.")
                return

        checkpoint = control.initial_load_checkpoint or {}
        offset = checkpoint.get("offset", 0)
        total_processed = checkpoint.get("processed", 0)
        
        control.initial_load_status = 'running'
        control.initial_load_started_at = control.initial_load_started_at or datetime.now(timezone.utc)
        self.db.commit()
        
        job = SyncJob(entity=ENTITY, job_type='initial', status='running', 
                      date_from=datetime(2025, 1, 1, tzinfo=timezone.utc), date_to=datetime.now(timezone.utc))
        self.db.add(job)
        self.db.commit()
        
        try:
            # Sync ALL 2025
            date_from = "2025-01-01T00:00:00.000-00:00"
            date_to = datetime.now(timezone.utc).isoformat()
            
            has_more = True
            created = 0
            updated = 0
            failed = 0
            
            while has_more:
                logger.info(f"[InitialLoad] Fetching orders offset {offset}...")
                
                params = {
                    "seller": seller_id,
                    "order.date_created.from": date_from,
                    "order.date_created.to": date_to,
                    "sort": "date_asc",
                    "offset": offset,
                    "limit": BATCH_SIZE
                }
                
                resp = self.ml_api.request('GET', '/orders/search', params=params)
                if resp.status_code != 200:
                    raise Exception(f"API Error {resp.status_code}: {resp.text}")
                    
                data = resp.json()
                orders = data.get('results', [])
                paging = data.get('paging', {})
                total = paging.get('total', 0)
                
                if not orders:
                    has_more = False
                    break
                    
                for order_data in orders:
                    try:
                        detail_resp = self.ml_api.request('GET', f"/orders/{order_data['id']}")
                        if detail_resp.status_code == 200:
                            full_order = detail_resp.json()
                            res = self._upsert_order(full_order)
                            if res == 'created': created += 1
                            else: updated += 1
                        else:
                            failed += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing order {order_data['id']}: {e}")
                        failed += 1
                    
                    total_processed += 1
                
                self.db.commit()
                
                offset += len(orders)
                control.initial_load_checkpoint = {"offset": offset, "processed": total_processed}
                control.initial_load_processed_records = total_processed
                control.initial_load_total_records = total
                self.db.commit()
                
                time.sleep(0.5)
                
                if offset >= total:
                    has_more = False
                    
            control.initial_load_status = 'completed'
            control.initial_load_completed_at = datetime.now(timezone.utc)
            
            job.status = 'completed'
            job.records_found = total_processed
            job.records_created = created
            job.records_updated = updated
            job.records_failed = failed
            job.finished_at = datetime.now(timezone.utc)
            
            self.db.commit()
            logger.info(f"[InitialLoad] Orders Completed. Total: {total_processed}")
            
            self.db.commit()
            logger.info(f"[InitialLoad] Orders Completed. Total: {total_processed}")
            
        except Exception as e:
            logger.error(f"[InitialLoad] Failed: {e}")
            self.db.rollback()
            
            # Robust Failure Logging
            try:
                if 'control' in locals() and control and control.id:
                    control = self.db.query(SyncControl).get(control.id)
                    if control: control.initial_load_status = 'failed'
                
                if 'job' in locals() and job and job.id:
                     job = self.db.query(SyncJob).get(job.id)
                     if job:
                         job.status = 'failed'
                         job.error_message = str(e)[:500]
                         job.finished_at = datetime.now(timezone.utc)
                
                self.db.commit()
            except Exception as ex:
                logger.error(f"Critical: Failed to log error state: {ex}")
                self.db.rollback()
            
            raise e

    def _upsert_order(self, data: dict):
        order_id = str(data.get('id'))
        existing = self.db.query(MlOrder).filter(MlOrder.ml_order_id == order_id).first()
        
        parsed = self._parse_order_data(data)
        
        status = 'updated'
        if not existing:
            existing = MlOrder(ml_order_id=order_id)
            self.db.add(existing)
            status = 'created'
            
        for k, v in parsed.items():
            setattr(existing, k, v)
        
        self._upsert_items(existing, data.get('order_items', []))
        
        return status

    def _upsert_items(self, order: MlOrder, items_data: list):
        for item in items_data:
             item_id = item.get('item', {}).get('id')
             if not item_id: continue
             
             existing_item = self.db.query(MlOrderItem).filter(
                 MlOrderItem.ml_order_id == order.ml_order_id,
                 MlOrderItem.ml_item_id == item_id
             ).first()
             
             if not existing_item:
                 new_item = MlOrderItem(
                     ml_order_id=order.ml_order_id,
                     ml_item_id=item_id,
                     title=item.get('item', {}).get('title'),
                     quantity=item.get('quantity'),
                     unit_price=item.get('unit_price'),
                     sale_fee=item.get('sale_fee'),
                     sku=item.get('item', {}).get('seller_sku')
                 )
                 self.db.add(new_item)
             else:
                 existing_item.quantity = item.get('quantity')
                 existing_item.unit_price = item.get('unit_price')
                 existing_item.sale_fee = item.get('sale_fee')
                 existing_item.sku = item.get('item', {}).get('seller_sku')

    def _parse_order_data(self, d: dict):
        def parse_dt(dt_str):
            if not dt_str: return None
            # Handle Z
            dt_str = dt_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(dt_str)
            # Normalize to UTC
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc)
            # Make Naive for DB
            return dt.replace(tzinfo=None)

        date_created = parse_dt(d.get('date_created'))
        date_closed = parse_dt(d.get('date_closed'))
        last_updated = parse_dt(d.get('last_updated'))
        
        buyer = d.get('buyer', {})
        shipping = d.get('shipping', {})
        
        return {
            "seller_id": str(d.get('seller', {}).get('id')),
            "status": d.get('status'),
            "status_detail": d.get('status_detail', {}).get('description') if isinstance(d.get('status_detail'), dict) else str(d.get('status_detail')),
            "total_amount": d.get('total_amount'),
            "paid_amount": d.get('paid_amount'),
            "currency_id": d.get('currency_id'),
            "buyer_id": str(buyer.get('id')),
            "buyer_nickname": buyer.get('nickname'),
            "buyer_first_name": buyer.get('first_name'),
            "buyer_last_name": buyer.get('last_name'),
            "shipping_id": str(shipping.get('id')),
            "shipping_status": shipping.get('status'),
            "date_created": date_created,
            "date_closed": date_closed,
            "last_updated": last_updated,
            "pack_id": str(d.get('pack_id')) if d.get('pack_id') else None,
            "tags": json.dumps(d.get('tags', [])),
            "raw_data": d
        }

    # -------------------------------------------------------------------------
    # ADS
    # -------------------------------------------------------------------------
    def load_ads(self):
        ENTITY = 'ads'
        seller_id = self._get_seller_id()
        if not seller_id: return

        control = self.db.query(SyncControl).filter(SyncControl.entity == ENTITY).first()
        if not control:
            control = SyncControl(entity=ENTITY)
            self.db.add(control)
            self.db.commit()

        if control.initial_load_status == 'running':
             if control.updated_at and (datetime.now(timezone.utc) - control.updated_at).seconds > 3600:
                logger.warning("Resuming stale ads job...")
             else:
                logger.warning("Initial load already running for ads.")
                return

        checkpoint = control.initial_load_checkpoint or {}
        scroll_id = checkpoint.get("scroll_id", None)
        total_processed = checkpoint.get("processed", 0)

        control.initial_load_status = 'running'
        control.initial_load_started_at = control.initial_load_started_at or datetime.now(timezone.utc)
        
        job = SyncJob(entity=ENTITY, job_type='initial', status='running', 
                      date_from=datetime(2025, 1, 1, tzinfo=timezone.utc), date_to=datetime.now(timezone.utc))
        self.db.add(job)
        self.db.commit()

        try:
            has_more = True
            created = 0
            updated = 0
            failed = 0
            
            while has_more:
                logger.info(f"[InitialLoad] Fetching ads scroll_id {scroll_id}...")
                
                params = {
                    "search_type": "scan",
                    "status": "active",
                    "limit": 100
                }
                if scroll_id:
                    params["scroll_id"] = scroll_id
                
                resp = self.ml_api.request('GET', f"/users/{seller_id}/items/search", params=params)
                if resp.status_code != 200:
                    raise Exception(f"API Error {resp.status_code}: {resp.text}")
                
                data = resp.json()
                results = data.get("results", [])
                
                new_scroll_id = data.get("scroll_id") or data.get("paging", {}).get("scroll_id")
                
                if not results:
                    has_more = False
                    break
                
                # Fetch Output
                chunk_size = 20
                for i in range(0, len(results), chunk_size):
                    chunk_ids = results[i:i+chunk_size]
                    ids_str = ",".join(chunk_ids)
                    
                    details_resp = self.ml_api.request('GET', "/items", params={"ids": ids_str})
                    if details_resp.status_code == 200:
                        items_data = details_resp.json()
                        for item_wrap in items_data:
                            if item_wrap.get("code") == 200:
                                res = self._upsert_ad(item_wrap.get("body"))
                                if res == 'created': created += 1
                                else: updated += 1
                            else:
                                failed += 1
                    else:
                        logger.error(f"Failed to fetch ad details chunk")
                        failed += len(chunk_ids)
                        
                    total_processed += len(chunk_ids)
                
                self.db.commit() 
                
                scroll_id = new_scroll_id
                control.initial_load_checkpoint = {"scroll_id": scroll_id, "processed": total_processed}
                control.initial_load_processed_records = total_processed
                if data.get("paging", {}).get("total"):
                    control.initial_load_total_records = data.get("paging").get("total")
                
                self.db.commit()
                
                time.sleep(0.5)

            control.initial_load_status = 'completed'
            control.initial_load_completed_at = datetime.now(timezone.utc)
            
            job.status = 'completed'
            job.records_found = total_processed
            job.records_created = created
            job.records_updated = updated
            job.records_failed = failed
            job.finished_at = datetime.now(timezone.utc)
            
            self.db.commit()
            logger.info(f"[InitialLoad] Ads Completed. Total: {total_processed}")

            self.db.commit()
            logger.info(f"[InitialLoad] Ads Completed. Total: {total_processed}")

        except Exception as e:
            logger.error(f"[InitialLoad] Ads Failed: {e}")
            self.db.rollback()
            
            try:
                if 'control' in locals() and control and control.id:
                     control = self.db.query(SyncControl).get(control.id)
                     if control: control.initial_load_status = 'failed'
                
                if 'job' in locals() and job and job.id:
                     job = self.db.query(SyncJob).get(job.id)
                     if job:
                         job.status = 'failed'
                         job.error_message = str(e)[:500]
                         job.finished_at = datetime.now(timezone.utc)
                self.db.commit()
            except Exception as ex:
                 logger.error(f"Critical: Failed to log ads error state: {ex}")
                 self.db.rollback()
                 
            raise e

    def _upsert_ad(self, data: dict):
        item_id = data.get('id')
        existing = self.db.query(Ad).filter(Ad.id == item_id).first()
        
        parsed = self._parse_ad_data(data)
        
        status = 'updated'
        if not existing:
            existing = Ad(id=item_id)
            self.db.add(existing)
            status = 'created'
            
        for k, v in parsed.items():
            setattr(existing, k, v)
        
        self._upsert_variations(existing, data.get('variations', []))
        
        return status

    def _parse_ad_data(self, d: dict):
         def parse_dt(dt_str):
            if not dt_str: return None
            dt_str = dt_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc)
            return dt.replace(tzinfo=None)

         date_created = parse_dt(d.get('date_created'))
         last_updated = parse_dt(d.get('last_updated'))
         start_time = parse_dt(d.get('start_time'))
         stop_time = parse_dt(d.get('stop_time'))
         
         pictures = d.get('pictures', [])
         thumbnail = pictures[0].get('secure_url') if pictures else d.get('thumbnail')
         
         attributes = d.get('attributes', [])
         
         return {
             "title": d.get('title'),
             "subtitle": d.get('subtitle'),
             "category_name": d.get('category_id'),
             "price": d.get('price'),
             "original_price": d.get('original_price'),
             "currency_id": d.get('currency_id'),
             "available_quantity": d.get('available_quantity'),
             "sold_quantity": d.get('sold_quantity'),
             "status": d.get('status'),
             "listing_type_id": d.get('listing_type_id'),
             "listing_type": d.get('listing_type_id'),
             "thumbnail": thumbnail,
             "pictures": [p.get('secure_url') for p in pictures],
             "attributes": attributes, 
             "seller_custom_field": d.get('seller_custom_field'),
             "sku": d.get('seller_custom_field'),
             "shipping_mode": d.get('shipping', {}).get('mode'),
             "free_shipping": d.get('shipping', {}).get('free_shipping'),
             "is_full": d.get('shipping', {}).get('logistic_type') == 'fulfillment',
             "permalink": d.get('permalink'),
             "date_created": date_created,
             "last_updated": last_updated,
             "start_time": start_time,
             "stop_time": stop_time,
             "raw_data": d
         }

    def _upsert_variations(self, ad: Ad, variations: list):
        for v in variations:
            v_id = str(v.get('id'))
            
            existing = self.db.query(AdVariation).filter(AdVariation.id == v_id).first()
            if not existing:
                existing = AdVariation(id=v_id, ad_id=ad.id)
                self.db.add(existing)
            
            existing.price = v.get('price')
            existing.available_quantity = v.get('available_quantity')
            existing.sku = v.get('seller_custom_field') or v.get('id') # Fallback if no SKU
            existing.seller_custom_field = v.get('seller_custom_field')
            existing.picture_ids = v.get('picture_ids')
            existing.attribute_combination = self._get_flattened_attributes(v.get('attribute_combinations', []))

    def _get_flattened_attributes(self, attrs: list):
        if not attrs: return None
        return ", ".join([f"{a.get('name')}: {a.get('value_name')}" for a in attrs])
