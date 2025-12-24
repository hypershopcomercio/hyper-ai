"""
Webhook Processor - Handles queued webhook events asynchronously.
Fetches order details from ML API and updates the database.
"""
import logging
import threading
import time
from queue import Empty
from datetime import datetime

logger = logging.getLogger(__name__)


class WebhookProcessor:
    """
    Background worker that processes webhook events from the queue.
    """
    
    def __init__(self, webhook_queue, db_session_factory, meli_service_factory):
        """
        Args:
            webhook_queue: Queue instance with webhook events
            db_session_factory: Callable that returns a new DB session
            meli_service_factory: Callable that returns a MeliApiService instance
        """
        self.queue = webhook_queue
        self.db_session_factory = db_session_factory
        self.meli_service_factory = meli_service_factory
        self.running = False
        self.thread = None
        self.processed_count = 0
        self.error_count = 0
        self.last_processed_at = None
        
        # SSE subscribers for real-time updates
        self.subscribers = []
    
    def start(self):
        """Start the background processor thread."""
        if self.running:
            logger.warning("[WEBHOOK_PROCESSOR] Already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        logger.info("[WEBHOOK_PROCESSOR] Started")
    
    def stop(self):
        """Stop the background processor."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("[WEBHOOK_PROCESSOR] Stopped")
    
    def _process_loop(self):
        """Main processing loop."""
        while self.running:
            try:
                # Wait for an event with timeout
                event = self.queue.get(timeout=1)
                self._process_event(event)
            except Empty:
                # No events, continue waiting
                continue
            except Exception as e:
                logger.error(f"[WEBHOOK_PROCESSOR] Error in loop: {e}")
                self.error_count += 1
                time.sleep(1)  # Backoff on error
    
    def _process_event(self, event):
        """Process a single webhook event."""
        topic = event.get('topic')
        resource = event.get('resource', '')
        
        logger.info(f"[WEBHOOK_PROCESSOR] Processing: {topic} -> {resource}")
        
        try:
            if topic == 'orders_v2':
                self._handle_order_event(resource)
            elif topic == 'items':
                self._handle_item_event(resource)
            elif topic == 'payments':
                self._handle_payment_event(resource)
            else:
                logger.info(f"[WEBHOOK_PROCESSOR] Ignored topic: {topic}")
            
            self.processed_count += 1
            self.last_processed_at = datetime.utcnow()
            
            # Broadcast to SSE clients
            try:
                from app.api.endpoints.sse import broadcast_event
                broadcast_event('webhook_processed', {
                    'topic': topic,
                    'resource': resource,
                    'timestamp': self.last_processed_at.isoformat()
                })
            except Exception as sse_err:
                logger.warning(f"[WEBHOOK_PROCESSOR] SSE broadcast failed: {sse_err}")
            
            # Sync visits to update real-time metrics (visits, conversion)
            try:
                self._sync_visits_for_update()
            except Exception as visits_err:
                logger.warning(f"[WEBHOOK_PROCESSOR] Visits sync failed: {visits_err}")
            
            # Notify internal subscribers (legacy)
            self._notify_subscribers({
                'type': 'webhook_processed',
                'topic': topic,
                'resource': resource,
                'timestamp': self.last_processed_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"[WEBHOOK_PROCESSOR] Error processing {topic}: {e}")
            self.error_count += 1
    
    def _handle_order_event(self, resource):
        """
        Handle orders_v2 topic.
        Resource format: /orders/{order_id}
        """
        # Extract order ID from resource
        order_id = resource.replace('/orders/', '').strip()
        if not order_id:
            logger.warning("[WEBHOOK_PROCESSOR] Invalid order resource")
            return
        
        logger.info(f"[WEBHOOK_PROCESSOR] Fetching order: {order_id}")
        
        # Get DB session and ML service
        db = self.db_session_factory()
        meli = self.meli_service_factory(db)
        
        try:
            # Fetch order from ML API using the correct method
            order_data = meli.get_order(order_id)
            
            if order_data:
                # Upsert order using existing sync logic
                from app.services.sync_engine import SyncEngine
                engine = SyncEngine()  # Creates its own DB session
                engine._process_order_full(order_data)
                engine.db.commit()
                engine.db.close()
                logger.info(f"[WEBHOOK_PROCESSOR] Order {order_id} synced successfully")
            else:
                logger.warning(f"[WEBHOOK_PROCESSOR] Order {order_id} not found in API")
                
        except Exception as e:
            logger.error(f"[WEBHOOK_PROCESSOR] Error syncing order {order_id}: {e}")
            raise
        finally:
            db.close()
    
    def _handle_item_event(self, resource):
        """
        Handle items topic.
        Resource format: /items/{item_id}
        """
        item_id = resource.replace('/items/', '').strip()
        if not item_id:
            return
        
        logger.info(f"[WEBHOOK_PROCESSOR] Item update: {item_id}")
        
        # For items, we can trigger a targeted ad sync
        # This is lower priority than orders
        db = self.db_session_factory()
        meli = self.meli_service_factory(db)
        
        try:
            # Use the request method with GET
            item_data = meli.request('GET', f'/items/{item_id}')
            if item_data:
                from app.services.sync_engine import SyncEngine
                engine = SyncEngine()  # Creates its own DB session
                engine._upsert_ad(item_data)
                engine.db.commit()
                engine.db.close()
                logger.info(f"[WEBHOOK_PROCESSOR] Item {item_id} synced")
        except Exception as e:
            logger.error(f"[WEBHOOK_PROCESSOR] Error syncing item {item_id}: {e}")
        finally:
            db.close()
    
    def _handle_payment_event(self, resource):
        """
        Handle payments topic.
        Resource format: /collections/{payment_id} or /payments/{payment_id}
        """
        # Payments can trigger order status updates
        # We extract the payment ID and find the associated order
        logger.info(f"[WEBHOOK_PROCESSOR] Payment update: {resource}")
        # For now, log only - full implementation would fetch payment and update order
    
    def _notify_subscribers(self, data):
        """Notify all SSE subscribers of an update."""
        for subscriber in self.subscribers[:]:
            try:
                subscriber(data)
            except Exception:
                self.subscribers.remove(subscriber)
    
    def add_subscriber(self, callback):
        """Add an SSE subscriber."""
        self.subscribers.append(callback)
    
    def remove_subscriber(self, callback):
        """Remove an SSE subscriber."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def _sync_visits_for_update(self):
        """
        Sync visits data from ML API to update real-time metrics.
        This ensures visits and conversion rates are updated when webhooks arrive.
        """
        from datetime import date, timedelta
        from app.models.ml_metrics_daily import MlMetricsDaily
        from app.models.ad import Ad
        import os
        
        logger.info("[WEBHOOK_PROCESSOR] Syncing visits for real-time update...")
        
        db = self.db_session_factory()
        meli = self.meli_service_factory(db)
        
        try:
            user_id = os.getenv('MELI_USER_ID')
            if not user_id:
                logger.warning("[WEBHOOK_PROCESSOR] MELI_USER_ID not set")
                return
            
            # Get items to sync visits for (active items only, limit for performance)
            items = db.query(Ad).filter(Ad.status == 'active').limit(20).all()
            
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            for item in items:
                try:
                    # Fetch visits from ML API
                    visits_data = meli.request(
                        'GET', 
                        f'/items/{item.id}/visits/time_window',
                        params={'last': 7, 'unit': 'day'}
                    )
                    
                    if visits_data and isinstance(visits_data, list):
                        for visit_entry in visits_data:
                            visit_date = visit_entry.get('date')
                            if visit_date:
                                visit_date_obj = date.fromisoformat(visit_date[:10])
                                total_visits = visit_entry.get('total', 0)
                                
                                # Upsert to ml_metrics_daily
                                existing = db.query(MlMetricsDaily).filter(
                                    MlMetricsDaily.item_id == item.id,
                                    MlMetricsDaily.date == visit_date_obj
                                ).first()
                                
                                if existing:
                                    existing.visits = total_visits
                                else:
                                    new_metric = MlMetricsDaily(
                                        item_id=item.id,
                                        date=visit_date_obj,
                                        visits=total_visits,
                                        sales_qty=0
                                    )
                                    db.add(new_metric)
                    
                except Exception as item_err:
                    logger.debug(f"[WEBHOOK_PROCESSOR] Visits sync error for {item.id}: {item_err}")
                    continue
            
            db.commit()
            logger.info("[WEBHOOK_PROCESSOR] Visits sync completed")
            
        except Exception as e:
            logger.error(f"[WEBHOOK_PROCESSOR] Visits sync error: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_status(self):
        """Get processor status."""
        return {
            'running': self.running,
            'queue_size': self.queue.qsize(),
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'last_processed_at': self.last_processed_at.isoformat() if self.last_processed_at else None
        }


# Global processor instance (initialized in run_web.py)
_processor = None


def get_processor():
    """Get the global webhook processor instance."""
    return _processor


def init_processor(webhook_queue, db_session_factory, meli_service_factory):
    """Initialize the global webhook processor."""
    global _processor
    _processor = WebhookProcessor(webhook_queue, db_session_factory, meli_service_factory)
    return _processor
