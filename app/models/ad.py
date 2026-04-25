from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Ad(Base):
    __tablename__ = "ads"

    id = Column(String(255), primary_key=True, index=True) # ML Item ID (MLB...)
    seller_id = Column(String(255), index=True)
    title = Column(String(500))
    price = Column(Float)
    currency_id = Column(String(50))
    available_quantity = Column(Integer)
    sold_quantity = Column(Integer)
    status = Column(String(100))
    listing_type_id = Column(String(100), nullable=True) # gold_pro, gold_special
    listing_type = Column(String(100), nullable=True) # Legacy or descriptive
    category_name = Column(String(255), nullable=True)
    permalink = Column(String(1000))
    thumbnail = Column(String(1000))
    pictures = Column(JSON, nullable=True)
    attributes = Column(JSON, nullable=True)
    video_id = Column(String(255), nullable=True) # YouTube Video ID
    short_description = Column(String(1000), nullable=True) # Clips/Summary content
    manual_video_verified = Column(Boolean, default=False) # Manual override for Clips
    
    # Prices
    original_price = Column(Float, nullable=True) # The "DE" price (from Standard API or Prices API)
    promotion_price = Column(Float, nullable=True) # The "POR" price if different from price/base, or specific active promo

    
    # Shipping & Fulfillment
    free_shipping = Column(Boolean, default=False)
    shipping_mode = Column(String(100), nullable=True) # me2, etc
    is_full = Column(Boolean, default=False)
    is_catalog = Column(Boolean, default=False)
    health_score = Column(Float, default=0.0) # 0-100 or 0-1
    health = Column(Float, nullable=True) # Alias or specific field from migration
    
    sku = Column(String(255), index=True, nullable=True)
    gtin = Column(String(255), index=True, nullable=True)
    
    # Tiny Data
    cost = Column(Float, nullable=True)
    weight_g = Column(Float, nullable=True)
    length_mm = Column(Float, nullable=True)
    width_mm = Column(Float, nullable=True)
    height_mm = Column(Float, nullable=True)
    tiny_id = Column(String(255), nullable=True)

    # Margin Calculation
    margin_percent = Column(Float, nullable=True)
    margin_value = Column(Float, nullable=True)
    is_margin_alert = Column(Boolean, default=False)
    commission_percent = Column(Float, nullable=True)
    
    # Financial Details
    commission_cost = Column(Float, default=0.0) 
    shipping_cost = Column(Float, default=0.0)
    tax_cost = Column(Float, default=0.0)
    ads_spend_30d = Column(Float, default=0.0)
    
    # Margin Defense
    target_margin = Column(Float, nullable=True) # User defined target (0.15 for 15%)
    suggested_price = Column(Float, nullable=True) # Calculated price to reach target
    strategy_start_price = Column(Float, nullable=True) # Price when strategy was activated
    current_step_number = Column(Integer, default=0) # Current step in the pricing plan (0 = not started)

    # Metrics Snapshot
    visits_30d = Column(Integer, default=0)
    sales_30d = Column(Integer, default=0)
    visits_7d_change = Column(Float, nullable=True) # Percentage change
    sales_7d_change = Column(Float, nullable=True) # Percentage change
    days_of_stock = Column(Float, nullable=True) # Estimated days left
    visits_last_updated = Column(DateTime(timezone=True), nullable=True)
    total_visits = Column(Integer, default=0)
    
    # Stock Control
    stock_tiny = Column(Integer, default=0)
    stock_divergence = Column(Integer, default=0)
    stock_incoming = Column(Integer, default=0) # Stock in transit/processing (Full)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime, nullable=True) # Sync timestamp
    
    # Hyper Sync 2.0 New Files
    subtitle = Column(String(500))
    seller_custom_field = Column(String(255))
    start_time = Column(DateTime(timezone=True))
    stop_time = Column(DateTime(timezone=True))
    raw_data = Column(JSON)     # Full payload backup

    # Relationships
    # variations = relationship("AdVariation", back_populates="ad", cascade="all, delete-orphan")

