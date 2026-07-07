from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AdsRecommendation(Base):
    """
    Fila de recomendações do motor de decisão de Ads (nível 1 da escada de
    autonomia — ver docs/ads-decision-engine.md).

    Ciclo: pending -> accepted|rejected|expired
           accepted -> executed|failed (execução só com ADS_WRITE_ENABLED=true)
    outcome: medido 7d após execução (feedback loop) comparando janelas
    antes/depois em ml_ads_item_daily.
    """
    __tablename__ = "ads_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50), nullable=False, index=True)
    action_code = Column(String(30), nullable=False)      # pausar | reduzir_ou_pausar | aumentar
    classification = Column(String(20))                   # queimando | prejuizo | atencao | escalar
    lifecycle_stage = Column(String(20))                  # lancamento | crescimento | maturidade | liquidacao
    reason = Column(Text)
    impact = Column(String(255))
    metrics_snapshot = Column(JSON)                       # spend, acos, clicks, margem etc no momento da geração

    status = Column(String(20), nullable=False, default="pending", index=True)
    created_at = Column(DateTime, server_default=func.now())
    decided_at = Column(DateTime, nullable=True)
    decided_by = Column(String(50), nullable=True)        # "user" | "auto"
    executed_at = Column(DateTime, nullable=True)
    execution_result = Column(Text, nullable=True)        # resposta da API ML ou motivo da falha

    outcome_measured_at = Column(DateTime, nullable=True)
    outcome = Column(JSON, nullable=True)                 # {before: {...}, after: {...}, verdict}
