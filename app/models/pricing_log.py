"""
Price Adjustment Log Model
Stores history of all automated price changes for audit and rollback purposes.
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from datetime import datetime
from app.core.database import Base


class PriceAdjustmentLog(Base):
    __tablename__ = "price_adjustment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String(50), ForeignKey("ads.id"), nullable=False, index=True)
    
    # Price values
    old_price = Column(Numeric(10, 2), nullable=False)
    new_price = Column(Numeric(10, 2), nullable=False)
    target_price = Column(Numeric(10, 2), nullable=True)  # Final goal price
    
    # Strategy info
    target_margin = Column(Numeric(5, 4), nullable=True)  # e.g., 0.195 = 19.5%
    step_number = Column(Integer, default=1)  # Which step in the plan (1, 2, 3...)
    total_steps = Column(Integer, default=1)
    
    # Execution details
    trigger_type = Column(String(20), default='scheduled')  # 'scheduled', 'manual', 'retry'
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    # Status
    status = Column(String(20), default='pending')  # 'pending', 'success', 'failed', 'skipped', 'rolled_back'
    error_message = Column(Text, nullable=True)
    
    # For retry mechanism
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime, nullable=True)
