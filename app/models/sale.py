from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(String(255), primary_key=True) # Order ID
    date_created = Column(DateTime(timezone=True), index=True)
    seller_id = Column(String(255))
    item_id = Column(String(255), ForeignKey("ads.id"), index=True)
    status = Column(String(100))
    
    total_amount = Column(Float)
    currency_id = Column(String(50))
    
    quantity = Column(Integer)
    buyer_id = Column(String(255))
    
    # Financials (Realized)
    unit_price = Column(Float) # Price per unit sold
    shipping_cost = Column(Float, default=0.0) # Cost paid by seller for shipping
    commission_cost = Column(Float, default=0.0) # Meli fee
    tax_cost = Column(Float, default=0.0) # Taxes (DAS/DIFAL)
    product_cost = Column(Float, default=0.0) # COGS (from Tiny)
    marketing_cost = Column(Float, default=0.0) # Ads spend attribution (optional/advanced)
    
    total_cost = Column(Float, default=0.0) # Sum of all costs
    net_margin = Column(Float, default=0.0) # Profit value
    margin_percent = Column(Float, default=0.0) # Profit %
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

