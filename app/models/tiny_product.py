from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class TinyProduct(Base):
    __tablename__ = "tiny_products"

    id = Column(String(255), primary_key=True, index=True) # Tiny ID
    sku = Column(String(255), index=True)
    name = Column(String(500))
    cost = Column(Float) # Preço de Custo
    sale_price = Column(Float) # Preço de Venda (no Tiny)
    stock = Column(Integer) # Estoque (no Tiny - Saldo)
    
    # Tax fields
    ncm = Column(String(50), nullable=True)
    origin = Column(String(50), nullable=True) # 0, 1, 2...
    supplier_name = Column(String(255), nullable=True) # Fornecedor

    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
