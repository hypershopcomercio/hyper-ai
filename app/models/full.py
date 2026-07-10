"""
Modelos do módulo Full (Fulfillment do Mercado Livre).

Fase 1 (read-only): snapshot do estoque no Full por unidade de inventário,
série histórica diária e a tabela oficial de tarifas cadastrada em Settings.
O custo real derivado destas tabelas alimenta ProductFinancialMetric
(campos storage_cost / daily_storage_fee / inbound_freight_cost / storage_risk_cost),
que ads.py já consome no cálculo de margem do modal do produto.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Numeric, Date, JSON, Index
from datetime import datetime
from app.core.database import Base


class FullInventory(Base):
    """
    Snapshot ATUAL do estoque de um item no Full. 1 linha por inventory_id.
    Alimentado por MeliApiService.get_fulfillment_stock (read-only).
    """
    __tablename__ = "full_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_id = Column(String(64), unique=True, index=True, nullable=False)
    ad_id = Column(String(255), index=True, nullable=True)   # MLB do anúncio
    sku = Column(String(255), index=True, nullable=True)
    variation_id = Column(String(64), nullable=True)         # variação (Full é por variação)

    available_qty = Column(Integer, default=0)      # disponível para venda no CD
    in_transit_qty = Column(Integer, default=0)     # status 'transfer' — a caminho do CD (inbound)
    not_available_qty = Column(Integer, default=0)  # avariado/perdido/retido (não vendável)
    total_qty = Column(Integer, default=0)

    days_of_stock = Column(Float, nullable=True)        # cobertura estimada (disp. ÷ venda/dia)
    oldest_stock_days = Column(Integer, nullable=True)  # antiguidade aprox. do lote mais velho

    raw = Column(JSON, nullable=True)               # payload cru do /stock/fulfillment (auditoria)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FullStockDaily(Base):
    """Série histórica diária por inventory_id — base para tendência e antiguidade."""
    __tablename__ = "full_stock_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_id = Column(String(64), index=True, nullable=False)
    sku = Column(String(255), index=True, nullable=True)
    ad_id = Column(String(255), index=True, nullable=True)
    day = Column(Date, index=True, nullable=False)

    available_qty = Column(Integer, default=0)
    in_transit_qty = Column(Integer, default=0)
    not_available_qty = Column(Integer, default=0)

    __table_args__ = (
        Index("ix_full_stock_daily_inv_day", "inventory_id", "day", unique=True),
    )


class FullStorageTariff(Base):
    """
    Tabela oficial de tarifas do Full, cadastrada pelo usuário em Settings.
    O motor de custo casa o volume real do produto (dims do Ad) com a faixa
    e aplica daily_fee/inbound_fee + sobretaxa de estoque antigo.
    """
    __tablename__ = "full_storage_tariffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)          # rótulo da faixa (ex.: "Pequeno")
    min_volume_l = Column(Float, default=0.0)          # litros — limite inferior (>=)
    max_volume_l = Column(Float, nullable=True)        # litros — limite superior (<); NULL = sem teto

    daily_fee = Column(Numeric(10, 4), default=0.0)    # R$/unidade/dia de armazenagem
    inbound_fee = Column(Numeric(10, 2), default=0.0)  # R$/unidade de envio ao CD (inbound)

    aged_days_threshold = Column(Integer, default=90)  # a partir de N dias -> estoque antigo
    aged_daily_factor = Column(Float, default=3.0)     # multiplicador da diária após o limiar

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
