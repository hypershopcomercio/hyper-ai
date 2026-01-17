import logging
import warnings
from datetime import datetime, timedelta
import numpy as np
from app.core.database import SessionLocal
from app.models.competitor_intelligence import CompetitorImpactEvent, CompetitorMetricsHistory
from app.services.impact_analyzer import ImpactAnalyzer
from app.models.competitor_ad import CompetitorAd

# Suprimir warnings do numpy
warnings.simplefilter('ignore', RuntimeWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def to_float(val):
    try:
        if val is None: return 0.0
        # Check for NaN (float('nan') != float('nan'))
        if isinstance(val, float) and val != val: return 0.0
        return float(val)
    except: return 0.0

def to_int(val):
    try:
        if val is None: return 0
        if isinstance(val, float) and val != val: return 0
        return int(float(val))
    except: return 0

def generate_promo_insight():
    db = SessionLocal()
    try:
        # Buscar concorrentes com promoção ativa
        competitors = db.query(CompetitorAd).filter(CompetitorAd.original_price > CompetitorAd.price).all()
        
        analyzer = ImpactAnalyzer(db)
        
        for comp in competitors:
            # logger.info(pass) removido
            logger.info(f"Gerando insight para {comp.competitor_id} (Promo: {comp.price} < {comp.original_price})")
            
            # Verificar e limpar evento recente para forçar atualização com texto corrigido
            db.query(CompetitorImpactEvent).filter(
                CompetitorImpactEvent.competitor_id == comp.competitor_id,
                CompetitorImpactEvent.event_type == 'promotion_active'
            ).delete()
            db.commit()

            impact = {}
            try:
                raw_impact = analyzer.calculate_impact_on_our_sales(comp.ad_id, datetime.utcnow())
                # Sanitizar impact
                for k, v in raw_impact.items():
                    impact[k] = v 
            except Exception as e_imp:
                logger.error(f"Erro calculo impacto: {e_imp}")
                
            correlation = 0.0
            try:
                correlation = analyzer.calculate_correlation(comp.competitor_id, comp.ad_id)
            except Exception as e_corr:
                logger.error(f"Erro calculo correlacao: {e_corr}")
                
            discount_pct = 0.0
            if comp.original_price:
                discount_pct = ((comp.original_price - comp.price) / comp.original_price) * 100
            
            # Safety checks
            discount_pct_safe = to_float(discount_pct)
            correlation_safe = to_float(correlation)
            
            diagnosis = f"📢 CONCORRENTE EM PROMOÇÃO: Preço reduzido em {discount_pct_safe:.0f}% (De R$ {comp.original_price} por R$ {comp.price}). "
            diagnosis += f"Correlação com suas vendas: {correlation_safe:.2f}. "
            
            est_loss = to_int(impact.get('estimated_sales_lost'))
            period_loss = impact.get('period_after', 'período recente')
            
            if est_loss > 0:
                 diagnosis += f"Estimativa de {est_loss} vendas perdidas entre {period_loss}."
            else:
                 diagnosis += "Impacto nas vendas em monitoramento (evento recente)."
            
            recommendation = "💡 Desconto agressivo detectado. Monitore se suas vendas caem nas próximas 24h. Se sim, considere ativar cupom de desconto ou destacar entrega rápida."
            
            # Criar evento
            event = CompetitorImpactEvent(
                competitor_id=comp.competitor_id,
                our_ad_id=comp.ad_id,
                event_type='promotion_active',
                event_timestamp=datetime.utcnow(),
                competitor_metric_name='price',
                competitor_metric_before=to_float(comp.original_price),
                competitor_metric_after=to_float(comp.price),
                change_percentage=-discount_pct_safe,
                
                estimated_sales_lost=est_loss,
                our_sales_before=to_int(impact.get('our_sales_before')),
                our_sales_after=to_int(impact.get('our_sales_after')),
                our_visits_before=to_int(impact.get('our_visits_before')),
                our_visits_after=to_int(impact.get('our_visits_after')),
                our_conversion_before=to_float(impact.get('our_conversion_before')),
                our_conversion_after=to_float(impact.get('our_conversion_after')),
                
                correlation_score=correlation_safe,
                confidence_level='medium',
                threat_score=75,
                diagnosis=diagnosis,
                recommendation=recommendation
            )
            
            db.add(event)
            logger.info("✅ Evento criado com sucesso!")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Erro Geral: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_promo_insight()
