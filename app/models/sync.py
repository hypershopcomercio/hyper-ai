from sqlalchemy import Column, Integer, String, Boolean, DateTime, CheckConstraint, Index, Float, Text, JSON
from sqlalchemy.sql import func
from app.models.base import Base

class SyncControl(Base):
    __tablename__ = 'sync_control'

    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String(50), unique=True, nullable=False)  # 'orders', 'ads', 'visits', 'stock'

    # Initial Load Status
    initial_load_status = Column(String(20), default='pending')  # pending, running, completed, failed
    initial_load_started_at = Column(DateTime(timezone=True))
    initial_load_completed_at = Column(DateTime(timezone=True))
    initial_load_total_records = Column(Integer, default=0)
    initial_load_processed_records = Column(Integer, default=0)
    initial_load_checkpoint = Column(JSON)  # Stores {"offset": 1000, "scroll_id": "xyz"}

    # Incremental Sync Status
    last_incremental_sync = Column(DateTime(timezone=True))
    last_incremental_count = Column(Integer, default=0)

    # Webhook Status
    webhook_enabled = Column(Boolean, default=False)
    webhook_last_received = Column(DateTime(timezone=True))

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SyncJob(Base):
    __tablename__ = 'sync_jobs'

    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String(50), nullable=False)
    job_type = Column(String(20), nullable=False)  # 'initial', 'incremental', 'webhook'
    status = Column(String(20), nullable=False)    # 'running', 'completed', 'failed'

    # Period
    date_from = Column(DateTime(timezone=True))
    date_to = Column(DateTime(timezone=True))

    # Results
    records_found = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    # Metrics
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    error_message = Column(Text)
    error_details = Column(JSON)

class WebhookQueue(Base):
    __tablename__ = 'webhook_queue'

    id = Column(Integer, primary_key=True, index=True)
    
    # Payload Info
    topic = Column(String(100), nullable=False)     # orders_v2, items
    resource = Column(String(200), nullable=False)  # /orders/12345
    user_id = Column(Integer)
    application_id = Column(Integer)
    
    # Process Control
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Results
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    received_at = Column(DateTime(timezone=True), server_default=func.now())

# Indexes
Index('idx_sync_jobs_entity', SyncJob.entity)
Index('idx_sync_jobs_status', SyncJob.status)
Index('idx_webhook_queue_status', WebhookQueue.status)
