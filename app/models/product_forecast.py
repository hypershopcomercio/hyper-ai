"""
Hyper Forecast V2 - Product Forecast Model
Stores product-level metrics for intelligent forecasting
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Boolean
from app.models.base import Base


class ProductForecast(Base):
    """
    Product-level metrics for forecasting.
    Updated daily by sync job.
    """
    __tablename__ = 'product_forecast'
    
    id = Column(Integer, primary_key=True)
    
    # Product identification
    mlb_id = Column(String(20), unique=True, nullable=False, index=True)
    sku = Column(String(100), nullable=True, index=True)
    title = Column(String(500))
    thumbnail = Column(String(500))
    
    # Category
    category_ml = Column(String(100))           # Original ML category code (MLB1839)
    category_normalized = Column(String(50))    # Normalized: cooler, piscina, etc
    
    # Sales metrics (calculated from MlOrderItem)
    avg_units_7d = Column(Numeric(10, 2))       # Average units sold per day (7 days)
    avg_units_30d = Column(Numeric(10, 2))      # Average units sold per day (30 days)
    total_units_7d = Column(Integer)            # Total units sold in 7 days
    total_units_30d = Column(Integer)           # Total units sold in 30 days
    total_revenue_7d = Column(Numeric(12, 2))   # Total revenue in 7 days
    total_revenue_30d = Column(Numeric(12, 2))  # Total revenue in 30 days
    
    # Trend analysis
    trend = Column(String(10))                  # 'up', 'down', 'stable'
    trend_pct = Column(Numeric(5, 2))           # % change vs previous week
    
    # Stock info (from Ad or Tiny)
    stock_current = Column(Integer, default=0)
    stock_full = Column(Integer, default=0)     # If using Full
    stock_local = Column(Integer, default=0)    # From Tiny/Local
    stock_incoming = Column(Integer, default=0) # Units in transit/processing
    days_of_coverage = Column(Numeric(5, 1))    # stock / avg_units_7d
    stock_status = Column(String(20))           # 'ok', 'low', 'critical', 'stockout'
    
    # Pricing
    price = Column(Numeric(10, 2))
    cost = Column(Numeric(10, 2))
    margin_pct = Column(Numeric(5, 2))
    
    # ABC Classification
    curve = Column(String(1))                   # A, B, C
    curve_criteria = Column(String(20))         # 'revenue', 'volume'
    
    # Forecast output
    forecast_units_today = Column(Numeric(10, 2))
    forecast_revenue_today = Column(Numeric(12, 2))
    
    # Flags
    is_active = Column(Boolean, default=True)
    has_rupture_risk = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProductForecast {self.mlb_id}: {self.avg_units_7d}/day, stock={self.stock_current}>"


class CategoryMapping(Base):
    """
    Maps ML category codes to normalized category names.
    Allows assigning seasonal factors per category.
    """
    __tablename__ = 'category_mapping'
    
    id = Column(Integer, primary_key=True)
    
    # Original ML category
    category_ml = Column(String(100), unique=True, nullable=False, index=True)
    category_ml_name = Column(String(255))      # Full category name from ML
    
    # Normalized
    category_normalized = Column(String(50))    # User-defined name: cooler, piscina, etc
    
    # Seasonal multipliers
    multiplier_summer = Column(Numeric(4, 2), default=1.0)   # Verão (Dez-Fev)
    multiplier_winter = Column(Numeric(4, 2), default=1.0)   # Inverno (Jun-Ago)
    multiplier_fall = Column(Numeric(4, 2), default=1.0)     # Outono (Mar-Mai)
    multiplier_spring = Column(Numeric(4, 2), default=1.0)   # Primavera (Set-Nov)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CategoryMapping {self.category_ml} -> {self.category_normalized}>"
