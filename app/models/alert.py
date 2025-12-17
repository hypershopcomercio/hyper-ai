
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    severity = Column(String(20), index=True) # 'critical', 'high', 'medium', 'low'
    type = Column(String(50)) # 'margin', 'stock', 'token', 'sync'
    message = Column(String(255))
    details = Column(Text, nullable=True)
    status = Column(String(20), default='active') # 'active', 'resolved', 'ignored'
    
    ad_id = Column(String(50), nullable=True) # Optional link to Ad
    # Optimization: We don't necessarily need a strict ForeignKey relation if we just want the ID string, 
    # but strictly it should be ForeignKey('ads.id'). 
    # Let's keep it loose for flexibility or strictly if we want cascade. Loose is safer for now.
