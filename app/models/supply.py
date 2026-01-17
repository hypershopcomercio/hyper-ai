from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum

class PurchaseStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    SHIPPING = "shipping"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=True)
    contact_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    lead_time_days = Column(Integer, default=7) # Tempo médio em dias
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    orders = relationship("PurchaseOrder", back_populates="supplier")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    status = Column(String, default=PurchaseStatus.DRAFT) # Enum como string
    
    expected_date = Column(Date, nullable=True)
    received_date = Column(DateTime, nullable=True)
    
    total_cost = Column(Numeric(10, 2), default=0.0) # Soma dos itens
    additional_costs = Column(Numeric(10, 2), default=0.0) # Frete extra, taxas
    
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    supplier = relationship("Supplier", back_populates="orders")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    ad_id = Column(String, ForeignKey("ads.id"), nullable=True) # Pode ser nulo se comprarmos algo que não é Ad ainda? Melhor linkar com Ad ou Produto Base
    # Por simplificação, linkamos com Ad (SKU principal)
    
    sku = Column(String, nullable=False) # Redundância útil
    title = Column(String, nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    
    received_quantity = Column(Integer, default=0) # Para entregas parciais
    
    # Relacionamentos
    order = relationship("PurchaseOrder", back_populates="items")
    ad = relationship("app.models.ad.Ad") 

class InboundShipment(Base):
    """
    Representa uma remessa para o Full (Inbound).
    Agrupa custos de envio que devem ser rateados entre os itens.
    """
    __tablename__ = "inbound_shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True) # Ex: "Carga 05/01"
    status = Column(String, default="planning") # planning, shipped, received, closed
    
    shipping_cost = Column(Numeric(10, 2), default=0.0) # Custo do frete para o CD
    other_costs = Column(Numeric(10, 2), default=0.0)
    
    shipped_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos com StockBatch (um Inbound gera vários Batches no destino)
    batches = relationship("StockBatch", back_populates="inbound_shipment")

class StockBatch(Base):
    """
    Lote de estoque. Usado para FIFO e cálculo exato de margem.
    Cada entrada de estoque gera um Batch.
    """
    __tablename__ = "stock_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String, ForeignKey("ads.id"), nullable=False)
    
    initial_quantity = Column(Integer, nullable=False)
    remaining_quantity = Column(Integer, nullable=False)
    
    unit_product_cost = Column(Numeric(10, 2), nullable=False) # Custo do produto na NF
    unit_freight_cost = Column(Numeric(10, 2), default=0.0) # Rateio do frete de entrada (Inbound ou Compra)
    
    entry_date = Column(DateTime, default=datetime.utcnow)
    
    # Origem
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    inbound_shipment_id = Column(Integer, ForeignKey("inbound_shipments.id"), nullable=True)
    
    # Relacionamentos
    ad = relationship("app.models.ad.Ad")
    inbound_shipment = relationship("InboundShipment", back_populates="batches")
