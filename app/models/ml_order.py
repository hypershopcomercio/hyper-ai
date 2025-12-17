
from sqlalchemy import Column, String, Integer, Float, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MlOrder(Base):
    __tablename__ = "ml_orders"

    id = Column(Integer, primary_key=True, index=True)
    ml_order_id = Column(String(50), unique=True, nullable=False)
    seller_id = Column(String(50))
    status = Column(String(50))
    total_amount = Column(DECIMAL(12, 2))
    paid_amount = Column(DECIMAL(12, 2))
    currency_id = Column(String(10))
    buyer_id = Column(String(50))
    shipping_id = Column(String(50))
    shipping_cost = Column(DECIMAL(10, 2))
    date_created = Column(DateTime)
    date_closed = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship("MlOrderItem", back_populates="order")

class MlOrderItem(Base):
    __tablename__ = "ml_order_items"

    id = Column(Integer, primary_key=True, index=True)
    ml_order_id = Column(String(50), ForeignKey("ml_orders.ml_order_id"), nullable=False)
    ml_item_id = Column(String(50), nullable=False)
    sku = Column(String(100))
    title = Column(String(500))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(12, 2))
    sale_fee = Column(DECIMAL(12, 2))
    created_at = Column(DateTime, server_default=func.now())

    order = relationship("MlOrder", back_populates="items")
