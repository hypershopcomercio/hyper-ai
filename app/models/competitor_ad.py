from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class CompetitorAd(Base):
    __tablename__ = "competitor_ads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competitor_id = Column(String(255), index=True, nullable=False) # MLB ID
    ad_id = Column(String(255), ForeignKey("ads.id"), nullable=False)
    
    title = Column(String(500))
    price = Column(Float)
    original_price = Column(Float) # [NEW] Added for promotion display
    permalink = Column(String(1000))
    seller_name = Column(String(255))
    
    status = Column(String(100), default="active") # active, paused
    last_updated = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        UniqueConstraint('ad_id', 'competitor_id', name='_ad_competitor_uc'),
    )
    
    # Relationship to our Ad
    # ad = relationship("Ad", back_populates="competitors") 
