from sqlalchemy import Column, String, Integer, DateTime, Date, DECIMAL, UniqueConstraint, Index
from sqlalchemy.sql import func
from app.core.database import Base


class MlAdsItemDaily(Base):
    """
    Métrica REAL de Product Ads por item x dia (fonte: /product_ads/ads/search
    chamado com date_from == date_to). Substitui a distribuição uniforme fake
    de ml_ads_metrics para fins de atribuição por venda.
    """
    __tablename__ = "ml_ads_item_daily"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50), nullable=False)          # MLB...
    date = Column(Date, nullable=False)
    cost = Column(DECIMAL(12, 2), default=0)              # gasto de Ads no dia
    revenue = Column(DECIMAL(12, 2), default=0)           # receita atribuída a Ads (metric "amount")
    clicks = Column(Integer, default=0)
    prints = Column(Integer, default=0)
    units_quantity = Column(Integer, default=0)           # unidades vendidas via Ads (direct+indirect), 0 se API não retornar
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('item_id', 'date', name='uq_ads_item_daily_item_date'),
        Index('idx_ads_item_daily_date', 'date'),
        Index('idx_ads_item_daily_item', 'item_id'),
    )
