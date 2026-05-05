from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from datetime import datetime
from app.core.database import Base

class ProductCostLog(Base):
    __tablename__ = "product_cost_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(255), index=True, nullable=True)
    ml_item_id = Column(String(255), index=True, nullable=True)
    
    # Cost values
    old_cost = Column(Numeric(12, 2), nullable=True)
    new_cost = Column(Numeric(12, 2), nullable=False)
    
    # Metadata
    source = Column(String(50), default='manual') # 'manual', 'tiny_sync', 'bulk_import'
    changed_by = Column(String(100), nullable=True) # User ID or name
    notes = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
