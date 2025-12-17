
from sqlalchemy import Column, String, Integer, DateTime, Date, DECIMAL
from sqlalchemy.sql import func
from app.core.database import Base

class MlMetricsDaily(Base):
    __tablename__ = "ml_metrics_daily"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    visits = Column(Integer, default=0)
    sales_qty = Column(Integer, default=0)
    sales_revenue = Column(DECIMAL(12, 2), default=0)
    conversion_rate = Column(DECIMAL(5, 2))
    avg_price = Column(DECIMAL(12, 2))
    created_at = Column(DateTime, server_default=func.now())
