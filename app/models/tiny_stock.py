
from sqlalchemy import Column, String, Integer, Float, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.core.database import Base

class TinyStock(Base):
    __tablename__ = "tiny_stock"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), nullable=False)
    warehouse = Column(String(100))
    quantity = Column(Integer, default=0)
    reserved = Column(Integer, default=0)
    available = Column(Integer, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
