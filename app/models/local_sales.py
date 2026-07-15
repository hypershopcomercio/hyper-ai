"""Models for direct, over-the-counter sales and local pricing.

The Mercado Livre sales table represents imported marketplace orders.  Local
sales have a separate header/items structure so a physical receipt can contain
more than one SKU and can be cancelled without touching marketplace records.
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class SalesChannel(Base):
    __tablename__ = "sales_channels"

    id = Column(Integer, primary_key=True)
    key = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    channel_type = Column(String(30), nullable=False, default="online")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())


class LocalProductPrice(Base):
    __tablename__ = "local_product_prices"

    id = Column(Integer, primary_key=True)
    sku = Column(String(255), nullable=False, index=True)
    channel_key = Column(String(50), nullable=False, default="local", index=True)
    ad_id = Column(String(255), nullable=True, index=True)
    selling_price = Column(Float, nullable=False)
    target_margin_percent = Column(Float, nullable=False, default=10.0)
    calculated_cost = Column(Float, nullable=False, default=0.0)
    tax_rate_percent = Column(Float, nullable=False, default=0.0)
    is_manual_price = Column(Boolean, nullable=False, default=False)
    status = Column(String(30), nullable=False, default="ready")
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("sku", "channel_key", name="uq_local_product_price_sku_channel"),
    )


class LocalSale(Base):
    __tablename__ = "local_sales"

    id = Column(String(64), primary_key=True)
    channel_key = Column(String(50), nullable=False, default="local", index=True)
    customer_name = Column(String(255), nullable=True)
    payment_method = Column(String(80), nullable=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), nullable=False, default="completed", index=True)
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class LocalSaleItem(Base):
    __tablename__ = "local_sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(String(64), ForeignKey("local_sales.id"), nullable=False, index=True)
    sku = Column(String(255), nullable=False, index=True)
    product_name = Column(String(500), nullable=False)
    tiny_product_id = Column(String(255), nullable=True)
    ad_id = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False, default=0.0)
    target_margin_percent = Column(Float, nullable=False, default=0.0)
    tax_rate_percent = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    line_total = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(String(64), primary_key=True)
    sku = Column(String(255), nullable=False, index=True)
    movement_type = Column(String(50), nullable=False, index=True)
    quantity_delta = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=False)
    reference_id = Column(String(64), nullable=False, index=True)
    sync_status = Column(String(30), nullable=False, default="pending", index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
