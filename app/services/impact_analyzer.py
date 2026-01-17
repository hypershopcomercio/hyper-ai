"""
Detector e analisador de eventos de impacto competitivo.

Identifica mudanças significativas nos concorrentes e calcula correlação com nosso desempenho.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import numpy as np
from app.models.competitor_intelligence import (
    CompetitorMetricsHistory, 
    CompetitorImpactEvent,
    CompetitorThreatScore
)

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    Analisador de impacto competitivo.
    
    Detecta eventos, calcula correlações e gera diagnósticos automáticos.
    """
    
    # Thresholds para detecção de eventos
    PRICE_DROP_THRESHOLD = 5  # % de redução de preço para ser considerado evento
    SALES_SPIKE_THRESHOLD = 50  # % de aumento em vendas
    VISITS_SPIKE_THRESHOLD = 30  # % de aumento em visitas
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_price_change_event(
        self, 
        competitor_id: str, 
        our_ad_id: str,
        lookback_hours: int = 24
    ) -> Optional[Dict]:
        """
        Detecta mudança significativa de preço.
        """
        since = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        # Buscar últimas 2 métricas
        metrics = self.db.query(CompetitorMetricsHistory).filter(
            and_(
                CompetitorMetricsHistory.competitor_id == competitor_id,
                CompetitorMetricsHistory.our_ad_id == our_ad_id,
                CompetitorMetricsHistory.timestamp >= since
            )
        ).order_by(desc(CompetitorMetricsHistory.timestamp)).limit(2).all()
        
        if len(metrics) < 2:
            return None
        
        current, previous = metrics[0], metrics[1]
        
        if not current.price or not previous.price:
            return None
        
        change_pct = ((current.price - previous.price) / previous.price) * 100
        
        # Evento significativo?
        if abs(change_pct) >= self.PRICE_DROP_THRESHOLD:
            return {
                'event_type': 'price_drop' if change_pct < 0 else 'price_increase',
                'metric_before': float(previous.price),
                'metric_after': float(current.price),
                'change_percentage': change_pct,
                'timestamp': current.timestamp
            }
        
        return None
    
    def detect_sales_spike(
        self,
        competitor_id: str,
        our_ad_id: str,
        lookback_hours: int = 24
    ) -> Optional[Dict]:
        """
        Detecta spike de vendas do concorrente.
        """
        since = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        metrics = self.db.query(CompetitorMetricsHistory).filter(
            and_(
                CompetitorMetricsHistory.competitor_id == competitor_id,
                CompetitorMetricsHistory.our_ad_id == our_ad_id,
                CompetitorMetricsHistory.timestamp >= since
            )
        ).order_by(desc(CompetitorMetricsHistory.timestamp)).limit(2).all()
        
        if len(metrics) < 2:
            return None
        
        current, previous = metrics[0], metrics[1]
        
        if not current.sales or not previous.sales or previous.sales == 0:
            return None
        
        change_pct = ((current.sales - previous.sales) / previous.sales) * 100
        
        if change_pct >= self.SALES_SPIKE_THRESHOLD:
            return {
                'event_type': 'sales_spike',
                'metric_before': previous.sales,
                'metric_after': current.sales,
                'change_percentage': change_pct,
                'timestamp': current.timestamp
            }
        
        return None
    
    def calculate_impact_on_our_sales(
        self,
        our_ad_id: str,
        event_timestamp: datetime,
        window_days: int = 7
    ) -> Dict:
        """
        Calcula impacto nas nossas vendas após um evento do concorrente.
        
        Compara média de 7 dias antes vs após o evento.
        """
        before_start = event_timestamp - timedelta(days=window_days)
        before_end = event_timestamp
        after_start = event_timestamp
        after_end = event_timestamp + timedelta(days=window_days)
        
        # Buscar nossas métricas antes do evento
        before_metrics = self.db.query(CompetitorMetricsHistory).filter(
            and_(
                CompetitorMetricsHistory.our_ad_id == our_ad_id,
                CompetitorMetricsHistory.timestamp >= before_start,
                CompetitorMetricsHistory.timestamp < before_end
            )
        ).all()
        
        # Buscar nossas métricas depois do evento
        after_metrics = self.db.query(CompetitorMetricsHistory).filter(
            and_(
                CompetitorMetricsHistory.our_ad_id == our_ad_id,
                CompetitorMetricsHistory.timestamp >= after_start,
                CompetitorMetricsHistory.timestamp < after_end
            )
        ).all()
        
        # Validar dados suficientes (evitar comparação com futuro vazio)
        if not after_metrics:
            return {
                'estimated_sales_lost': 0,
                'status': 'insufficient_future_data',
                'period_before': f"{before_start.strftime('%d/%m')} a {before_end.strftime('%d/%m')}",
                'period_after': f"{after_start.strftime('%d/%m')} a {after_end.strftime('%d/%m')}"
            }

        # Calcular médias
        our_sales_before = np.mean([m.our_sales for m in before_metrics if m.our_sales]) if before_metrics else 0
        our_sales_after = np.mean([m.our_sales for m in after_metrics if m.our_sales]) if after_metrics else 0
        
        our_conv_before = np.mean([float(m.our_conversion_rate) for m in before_metrics if m.our_conversion_rate]) if before_metrics else 0
        our_conv_after = np.mean([float(m.our_conversion_rate) for m in after_metrics if m.our_conversion_rate]) if after_metrics else 0
        
        our_visits_before = np.mean([m.our_visits for m in before_metrics if m.our_visits]) if before_metrics else 0
        our_visits_after = np.mean([m.our_visits for m in after_metrics if m.our_visits]) if after_metrics else 0
        
        # Calcular vendas perdidas estimadas
        estimated_sales_lost = max(0, int(our_sales_before - our_sales_after))
        
        return {
            'our_sales_before': int(our_sales_before),
            'our_sales_after': int(our_sales_after),
            'our_conversion_before': round(our_conv_before, 2),
            'our_conversion_after': round(our_conv_after, 2),
            'our_visits_before': int(our_visits_before),
            'our_visits_after': int(our_visits_after),
            'estimated_sales_lost': estimated_sales_lost,
            'period_before': f"{before_start.strftime('%d/%m')} a {before_end.strftime('%d/%m')}",
            'period_after': f"{after_start.strftime('%d/%m')} a {after_end.strftime('%d/%m')}"
        }
    
    def calculate_correlation(
        self,
        competitor_id: str,
        our_ad_id: str,
        lookback_days: int = 30
    ) -> float:
        """
        Calcula correlação de Pearson entre vendas do concorrente e nossas vendas.
        
        Retorna valor entre -1 (correlação negativa perfeita) e 1 (correlação positiva perfeita).
        """
        since = datetime.utcnow() - timedelta(days=lookback_days)
        
        metrics = self.db.query(CompetitorMetricsHistory).filter(
            and_(
                CompetitorMetricsHistory.competitor_id == competitor_id,
                CompetitorMetricsHistory.our_ad_id == our_ad_id,
                CompetitorMetricsHistory.timestamp >= since,
                CompetitorMetricsHistory.sales.isnot(None),
                CompetitorMetricsHistory.our_sales.isnot(None)
            )
        ).all()
        
        if len(metrics) < 10:  # Mínimo de amostras
            return 0.0
        
        competitor_sales = [m.sales for m in metrics]
        our_sales = [m.our_sales for m in metrics]
        
        try:
            correlation = np.corrcoef(competitor_sales, our_sales)[0, 1]
            return round(correlation, 2)
        except:
            return 0.0
    
    def generate_diagnosis(self, event: Dict, impact: Dict, correlation: float) -> str:
        """
        Gera diagnóstico automático em texto natural com DATAS ESPECÍFICAS.
        """
        event_type = event['event_type']
        change_pct = event['change_percentage']
        sales_lost = impact.get('estimated_sales_lost', 0)
        period_after = impact.get('period_after', 'período recente')
        
        if event_type == 'price_drop':
            diagnosis = f"📢 CONCORRENTE REDUZIU PREÇO: Queda de {abs(change_pct):.1f}% "
            diagnosis += f"(de R${event['metric_before']:.2f} para R${event['metric_after']:.2f}). "
            
            if sales_lost > 0:
                diagnosis += f"Estimativa de {sales_lost} vendas perdidas entre {period_after}. "
            
            if correlation < -0.5:
                diagnosis += f"Alta correlação negativa ({correlation})."
            
        elif event_type == 'sales_spike':
            diagnosis = f"⚠️ SPIKE DE VENDAS: Concorrente cresceu +{change_pct:.1f}%. "
            
            if sales_lost > 0:
                diagnosis += f"Suas vendas caíram {sales_lost} un. no mesmo período ({period_after})."
        
        else:
             diagnosis = f"Evento {event_type} detectado."

        return diagnosis
    
    def generate_recommendation(self, event: Dict, impact: Dict) -> str:
        """
        Gera recomendação de ação.
        """
        event_type = event['event_type']
        change_pct = abs(event['change_percentage'])
        
        if event_type == 'price_drop' and change_pct > 10:
            return "💡 Recomendação: Considere ajustar seu preço para manter competitividade ou destacar diferenciais (frete grátis, qualidade, reviews)."
        
        elif event_type == 'sales_spike':
            return "💡 Recomendação: Investigue a causa do spike (promoção, anúncio patrocinado). Considere ações similares."
        
        return "💡 Continue monitorando a situação."
    
    def analyze_and_create_impact_event(
        self,
        competitor_id: str,
        our_ad_id: str,
        event: Dict
    ) -> bool:
        """
        Analisa evento detectado e cria registro de ImpactEvent com diagnóstico.
        """
        try:
            # Calcular impacto
            impact = self.calculate_impact_on_our_sales(
                our_ad_id, 
                event['timestamp']
            )
            
            # Calcular correlação
            correlation = self.calculate_correlation(competitor_id, our_ad_id)
            
            # Determinar nível de confiança
            if abs(correlation) > 0.7 and impact['estimated_sales_lost'] > 5:
                confidence = 'high'
                threat_score = 85
            elif abs(correlation) > 0.4 and impact['estimated_sales_lost'] > 2:
                confidence = 'medium'
                threat_score = 60
            else:
                confidence = 'low'
                threat_score = 30
            
            # Gerar diagnóstico e recomendação
            diagnosis = self.generate_diagnosis(event, impact, correlation)
            recommendation = self.generate_recommendation(event, impact)
            
            # Criar evento de impacto
            impact_event = CompetitorImpactEvent(
                competitor_id=competitor_id,
                our_ad_id=our_ad_id,
                event_type=event['event_type'],
                event_timestamp=event['timestamp'],
                competitor_metric_name='price' if 'price' in event['event_type'] else 'sales',
                competitor_metric_before=event['metric_before'],
                competitor_metric_after=event['metric_after'],
                change_percentage=event['change_percentage'],
                **impact,
                correlation_score=correlation,
                confidence_level=confidence,
                threat_score=threat_score,
                diagnosis=diagnosis,
                recommendation=recommendation
            )
            
            self.db.add(impact_event)
            self.db.commit()
            
            logger.info(f"✅ Evento de impacto criado: {event['event_type']} - {diagnosis}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar evento de impacto: {e}")
            self.db.rollback()
            return False
    
    def run_full_analysis(self, competitor_id: str, our_ad_id: str):
        """
        Executa análise completa para um concorrente.
        """
        logger.info(f"Iniciando análise de impacto para {competitor_id} vs {our_ad_id}")
        
        # Detectar eventos
        events = []
        
        price_event = self.detect_price_change_event(competitor_id, our_ad_id)
        if price_event:
            events.append(price_event)
        
        sales_event = self.detect_sales_spike(competitor_id, our_ad_id)
        if sales_event:
            events.append(sales_event)
        
        # Analisar cada evento
        for event in events:
            self.analyze_and_create_impact_event(competitor_id, our_ad_id, event)
        
        logger.info(f"Análise completa: {len(events)} eventos detectados")
