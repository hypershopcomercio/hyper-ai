from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class FixedCost(Base):
    """
    Representa um custo fixo recorrente da operação.
    Ex: Aluguel, Salários, Software.
    """
    __tablename__ = "financial_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False) # Valor mensal
    category = Column(String(50)) # operational, administrative, personnel, taxes
    
    # Configuração de recorrência
    active = Column(Boolean, default=True)
    day_of_month = Column(Integer, default=1) # Dia previsto de pagamento
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductFinancialMetric(Base):
    """
    Cache de métricas financeiras específicas de um produto (SKU).
    Calculado periodicamente (ex: job diário).
    """
    __tablename__ = "product_financial_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), index=True, nullable=False, unique=True) # Link com item/ad via SKU
    
    # Métricas de Devolução (Smart Risk)
    return_rate_90d = Column(Float, default=0.0) # Taxa de devolução (0.0 a 1.0)
    avg_return_cost = Column(Numeric(10, 2), default=0.0) # Custo médio por devolução (Frete + Avaria)
    
    # Métricas de Contribuição (Rateio)
    revenue_share_30d = Column(Float, default=0.0) # % da receita total da empresa (0.0 a 1.0)
    
    # Resultado do Rateio (Valor calculado para somar no custo)
    # Ex: Se revenue_share é 10% e Custo Fixo Total é 10k -> aloca 1k. 
    # fixed_cost_share = 1k / vendas_mensais
    calculated_fixed_cost_share = Column(Numeric(10, 2), default=0.0)
    
    # Custo de Armazenagem (Calculado por item/dia)
    storage_cost = Column(Numeric(10, 2), default=0.0)
    daily_storage_fee = Column(Numeric(10, 4), default=0.0) # Taxa diária calculada (ex: 0.007)
    inbound_freight_cost = Column(Numeric(10, 2), default=0.0) # Custo de envio para Full
    storage_risk_cost = Column(Numeric(10, 2), default=0.0) # Risco de Long-Term Storage
    
    last_calculated_at = Column(DateTime, default=datetime.utcnow)

    # Opcional: Relacionamento com Ad ou Item se SKU for chave
    # Mas como SKU pode estar em múltiplos Ads, manteremos desacoplado por hora
