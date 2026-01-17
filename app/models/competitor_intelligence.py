"""
Modelos para análise de inteligência competitiva.

Rastreamento de métricas, eventos e impactos de concorrentes.
"""
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base


class CompetitorMetricsHistory(Base):
    """
    Histórico completo de métricas de concorrentes.
    
    Armazena snapshots periódicos de todas as métricas disponíveis do concorrente,
    junto com nossas métricas no mesmo momento para permitir análise comparativa.
    """
    __tablename__ = 'competitor_metrics_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    competitor_id = Column(String(50), nullable=False, index=True)  # MLB ID do concorrente
    our_ad_id = Column(String(50), nullable=False, index=True)  # Nosso MLB ID
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    # ====================
    # Métricas do Concorrente
    # ====================
    price = Column(Numeric(10, 2))
    visits = Column(Integer)  # Visitas do anúncio (via API pública ML)
    sales = Column(Integer)  # Quantidade vendida (disponível publicamente)
    conversion_rate = Column(Numeric(5, 2))  # Calculado: sales / visits
    search_position = Column(Integer)  # Posição no ranking de busca
    has_free_shipping = Column(Boolean)
    has_promotion = Column(Boolean)  # Desconto, cupom, etc.
    stock_available = Column(Integer)
    rating = Column(Numeric(3, 2))  # Avaliação média (0-5)
    reviews_count = Column(Integer)  # Quantidade de reviews
    seller_reputation = Column(String(20))  # 'red', 'orange', 'yellow', 'light_green', 'green'
    
    # ====================
    # Nossas Métricas (Snapshot)
    # ====================
    our_price = Column(Numeric(10, 2))
    our_visits = Column(Integer)
    our_sales = Column(Integer)
    our_conversion_rate = Column(Numeric(5, 2))
    our_search_position = Column(Integer)
    
    def __repr__(self):
        return f"<CompetitorMetrics {self.competitor_id} @ {self.timestamp}>"


class CompetitorImpactEvent(Base):
    """
    Eventos de impacto competitivo detectados.
    
    Registra mudanças significativas do concorrente e o impacto medido em nossas métricas.
    Usado para análise de correlação e diagnósticos automáticos.
    """
    __tablename__ = 'competitor_impact_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    competitor_id = Column(String(50), nullable=False, index=True)
    our_ad_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # 'price_drop', 'promotion_start', 'stock_out', etc.
    event_timestamp = Column(DateTime, nullable=False, default=func.now())
    detected_at = Column(DateTime, nullable=False, default=func.now())  # Quando detectamos
    
    # ====================
    # Mudança no Concorrente
    # ====================
    competitor_metric_name = Column(String(50))  # 'price', 'visits', 'has_promotion', etc.
    competitor_metric_before = Column(Numeric(10, 2))
    competitor_metric_after = Column(Numeric(10, 2))
    change_percentage = Column(Numeric(6, 2))  # Variação percentual
    
    # ====================
    # Impacto Detectado em Nós (janela de 24h após evento)
    # ====================
    our_sales_before = Column(Integer)  # Média 7d antes do evento
    our_sales_after = Column(Integer)  # Média 7d após o evento
    our_conversion_before = Column(Numeric(5, 2))
    our_conversion_after = Column(Numeric(5, 2))
    our_visits_before = Column(Integer)
    our_visits_after = Column(Integer)
    
    # ====================
    # Análise
    # ====================
    estimated_sales_lost = Column(Integer)  # Vendas perdidas estimadas
    estimated_revenue_lost = Column(Numeric(10, 2))  # Receita perdida estimada
    correlation_score = Column(Numeric(3, 2))  # Coeficiente de correlação (-1 a 1)
    confidence_level = Column(String(20))  # 'low', 'medium', 'high'
    threat_score = Column(Integer)  # 0-100, score de ameaça competitiva
    diagnosis = Column(Text)  # Diagnóstico automático em texto
    recommendation = Column(Text)  # Recomendação de ação
    
    # Foi respondido? (ação tomada)
    action_taken = Column(Boolean, default=False)
    action_type = Column(String(50))  # 'price_match', 'promotion', 'ignore', etc.
    action_timestamp = Column(DateTime)
    
    def __repr__(self):
        return f"<ImpactEvent {self.event_type} by {self.competitor_id} @ {self.event_timestamp}>"


class CompetitorThreatScore(Base):
    """
    Score de ameaça competitiva agregado (atualizado diariamente).
    
    Combina múltiplos fatores para gerar um score único de ameaça por concorrente.
    Permite priorização rápida de monitoramento.
    """
    __tablename__ = 'competitor_threat_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    competitor_id = Column(String(50), nullable=False, index=True)
    our_ad_id = Column(String(50), nullable=False, index=True)
    calculated_at = Column(DateTime, nullable=False, default=func.now())
    
    # ====================
    # Componentes do Score (0-100 cada)
    # ====================
    price_advantage_score = Column(Integer)  # Quanto mais barato, maior o score
    conversion_advantage_score = Column(Integer)
    visits_advantage_score = Column(Integer)
    position_advantage_score = Column(Integer)  # Posição melhor no ranking
    reputation_advantage_score = Column(Integer)
    
    # ====================
    # Score Final
    # ====================
    total_threat_score = Column(Integer)  # 0-100
    threat_level = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    
    # Texto de resumo
    summary = Column(Text)  # "Este concorrente está 20% mais barato e tem conversão 2x maior"
    
    def __repr__(self):
        return f"<ThreatScore {self.competitor_id}: {self.total_threat_score}/100>"
