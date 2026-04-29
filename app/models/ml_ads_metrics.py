from sqlalchemy import Column, String, Integer, DateTime, Date, DECIMAL
from sqlalchemy.sql import func
from app.core.database import Base

class MlAdsMetric(Base):
    __tablename__ = "ml_ads_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, index=True)
    cost = Column(DECIMAL(12, 2), default=0)
    revenue = Column(DECIMAL(12, 2), default=0)
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
