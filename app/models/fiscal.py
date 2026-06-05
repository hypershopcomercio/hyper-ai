from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class MonthlyTaxConfig(Base):
    """
    Guarda as alíquotas mensais do Simples Nacional ou outro regime aplicável
    de forma geral para o mês.
    """
    __tablename__ = "monthly_tax_configs"

    id = Column(Integer, primary_key=True, index=True)
    reference_month = Column(String(7), unique=True, nullable=False, index=True) # Formato YYYY-MM
    full_das_rate = Column(Float, nullable=False) # Ex: 10.0
    das_without_icms_rate = Column(Float, nullable=False) # Ex: 4.83
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductTaxProfile(Base):
    """
    Perfil fiscal específico de cada produto ou anúncio.
    Substitui simulações manuais por parâmetros cadastrados reais.
    """
    __tablename__ = "product_tax_profiles"

    id = Column(Integer, primary_key=True, index=True)
    mlb_id = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=True, index=True)
    tiny_product_id = Column(Integer, nullable=True)
    
    product_origin = Column(Enum('nacional', 'importado', name='product_origin_enum'), nullable=False, default='nacional')
    origin_uf = Column(String(2), nullable=True)
    destination_uf_default = Column(String(2), nullable=True)
    
    ncm = Column(String(10), nullable=True)
    cest = Column(String(10), nullable=True)
    
    has_st = Column(Boolean, nullable=False, default=False)
    has_ipi = Column(Boolean, nullable=False, default=False)
    has_difal = Column(Boolean, nullable=False, default=False)
    
    mva_rate = Column(Float, nullable=True) # Exigido se has_st for True
    ipi_rate = Column(Float, nullable=True) # Exigido se has_ipi for True
    origin_icms_rate = Column(Float, nullable=True)
    destination_icms_rate = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductPurchaseCost(Base):
    """
    Guarda o custo real e o valor da NF dos produtos comprados,
    permitindo apuração fiscal correta da Substituição Tributária.
    """
    __tablename__ = "product_purchase_costs"

    id = Column(Integer, primary_key=True, index=True)
    mlb_id = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=True, index=True)
    
    real_cost = Column(Float, nullable=False)
    nf_value = Column(Float, nullable=True) # Exigido para cálculo de ST
    nf_percentage = Column(Float, nullable=True) # Automaticamente calculado ou mantido fixo
    
    freight_cost = Column(Float, nullable=True, default=0.0)
    packaging_cost = Column(Float, nullable=True, default=0.0)
    other_costs = Column(Float, nullable=True, default=0.0)
    
    supplier_name = Column(String(200), nullable=True)
    nf_number = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=True)
    data_source = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime, nullable=True, default=datetime.utcnow)
    effective_until = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
