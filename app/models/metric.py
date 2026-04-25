from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, UniqueConstraint
from app.core.database import Base

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String(255), ForeignKey("ads.id"), index=True)
    date = Column(Date, index=True)
    
    visits = Column(Integer, default=0)
    sales = Column(Integer, default=0)
    gross_revenue = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    ads_spend = Column(Float, default=0.0)


    # Composite unique constraint to prevent duplicate metrics for same ad/day
    __table_args__ = (
        UniqueConstraint('ad_id', 'date', name='uq_ad_date'),
    )
