import logging
import time
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.sync import SyncControl, SyncJob
from app.models.ml_order import MlOrder, MlOrderItem
from app.services.meli_api import MeliApiService
from app.services.sync_v2.initial_load import InitialLoadService # Reuse upsert logic

logger = logging.getLogger(__name__)

BATCH_SIZE = 50

class IncrementalSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.ml_api = MeliApiService(db)
        # Reuse logic from InitialLoadService for upserts
        self.loader = InitialLoadService(db, meli_client=self.ml_api)

    def _get_seller_id(self):
        return self.loader._get_seller_id()

    def _emit_sale_event(self, order_data):
        try:
            from app.api.endpoints.sse import broadcast_event
            order_items = order_data.get('order_items', [])
            first = order_items[0] if order_items else {}
            title = first.get('item', {}).get('title', 'Novo Pedido')
            
            broadcast_event('order_update', {
                'title': title,
                'status': 'created',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            logger.info(f"[Incremental] 🎉 SSE Notification sent for: {title}")
        except Exception as e:
            logger.warning(f"[Incremental] Failed to emit SSE: {e}")

    def sync_orders_incremental(self, lookback_hours: int = None):
        ENTITY = 'orders'
        seller_id = self._get_seller_id()
        if not seller_id: return

        control = self.db.query(SyncControl).filter(SyncControl.entity == ENTITY).first()
        if not control:
            # Should have been created by initial load, but safe to create
            control = SyncControl(entity=ENTITY)
            self.db.add(control)
        
        # Determine Time Window
        now = datetime.now(timezone.utc)
        
        # Start with the last stored checkpoint
        last_sync = control.last_incremental_sync
        
        # If we have a forced lookback (e.g. 48h), we want to ensure we cover AT LEAST that window.
        # But if the system stopped 5 days ago, last_sync will be older.
        # So we take the MINIMUM (Oldest) date between last_sync and (now - lookback).
        
        if lookback_hours:
            force_start = now - timedelta(hours=lookback_hours)
            if not last_sync or force_start < last_sync:
                last_sync = force_start
                logger.info(f"[Incremental] Smart Lookback: Extending start to {last_sync} (Forced {lookback_hours}h)")
            else:
                 logger.info(f"[Incremental] Smart Lookback: Keeping {last_sync} (Older than forced {lookback_hours}h)")
        
        if not last_sync:
            # Fallback: 48h ago (safety default)
            last_sync = now - timedelta(hours=48)
            
        # Add buffer (overlap) of 5 mins to miss nothing
        date_from_dt = last_sync - timedelta(minutes=5)
        date_from = date_from_dt.isoformat()
        date_to = now.isoformat()
        
        job = SyncJob(entity=ENTITY, job_type='incremental', status='running', 
                      date_from=date_from_dt, date_to=now)
        self.db.add(job)
        self.db.commit()
        
        logger.info(f"[Incremental] Syncing orders from {date_from}")
        
        try:
            total_processed = 0
            created = 0
            updated = 0
            failed = 0
            
            # For Incremental, volume is low, so we might just page until done.
            offset = 0
            has_more = True
            
            while has_more:
                params = {
                    "seller": seller_id,
                    "order.date_last_updated.from": date_from,
                    "order.date_last_updated.to": date_to,
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
                        # Full detail fetch
                        detail_resp = self.ml_api.request('GET', f"/orders/{order_data['id']}")
                        if detail_resp.status_code == 200:
                            full_order = detail_resp.json()
                            res = self.loader._upsert_order(full_order)
                            if res == 'created': 
                                created += 1
                                self._emit_sale_event(full_order)
                            else: updated += 1
                        else:
                            failed += 1
                    except Exception as e:
                        logger.error(f"Error upserting order {order_data['id']}: {e}")
                        failed += 1
                        
                    total_processed += 1
                    
                    # Log progress every batch
                    if total_processed % 50 == 0:
                        logger.info(f"[Incremental] Progress: {total_processed} orders processed...")
                
                self.db.commit()
                offset += len(orders)
                if offset >= total:
                    has_more = False
                    
            # Update Control
            control.last_incremental_sync = now
            control.last_incremental_count = total_processed
            
            job.status = 'completed'
            job.records_found = total_processed
            job.records_created = created
            job.records_updated = updated
            job.records_failed = failed
            job.finished_at = datetime.now(timezone.utc)
            
            self.db.commit()
            logger.info(f"[Incremental] Orders Finished. Processed: {total_processed}")
            
        except Exception as e:
            logger.error(f"[Incremental] Failed: {e}")
            self.db.rollback()
            
            if job and job.id:
                 job = self.db.query(SyncJob).get(job.id)
                 if job:
                     job.status = 'failed'
                     job.error_message = str(e)[:500]
                     job.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            raise e
