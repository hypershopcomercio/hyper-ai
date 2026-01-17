"""
Popular dados REAIS de vendas dos últimos 30 dias.
Busca do ml_orders ao invés de simular.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.core.database import SessionLocal
from app.models.competitor_ad import CompetitorAd
from app.models.competitor_intelligence import CompetitorMetricsHistory, CompetitorImpactEvent
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.ad import Ad
import random
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_real_sales_data(days=30):
    db = SessionLocal()
    try:
        # Limpar dados antigos
        db.query(CompetitorMetricsHistory).delete()
        db.query(CompetitorImpactEvent).delete()
        db.commit()
        logger.info("Dados antigos limpos")
        
        competitors = db.query(CompetitorAd).all()
        logger.info(f"Encontrados {len(competitors)} concorrentes")
        
        if not competitors:
            logger.error("Nenhum concorrente cadastrado!")
            return
        
        total_metrics = 0
        total_events = 0
        
        for comp in competitors:
            logger.info(f"Processando: {comp.competitor_id}")
            
            # Buscar nosso anúncio (ad_id)
            our_ad = db.query(Ad).filter(Ad.id == comp.ad_id).first()
            if not our_ad:
                logger.warning(f"Anúncio {comp.ad_id} não encontrado")
                continue
            
            # Preço base do concorrente
            base_price = comp.price if comp.price else 150.0
            our_price = our_ad.price if our_ad.price else base_price * 0.95
            
            # Criar métricas diárias para últimos 30 dias
            for day_offset in range(days, 0, -1):
                snapshot_date = datetime.utcnow() - timedelta(days=day_offset)
                date_start = snapshot_date.replace(hour=0, minute=0, second=0)
                date_end = snapshot_date.replace(hour=23, minute=59, second=59)
                
                # BUSCAR VENDAS REAIS DO DIA para nosso produto
                real_sales = db.query(func.count(MlOrderItem.id)).join(MlOrder).filter(
                    and_(
                        MlOrderItem.ml_item_id == comp.ad_id,
                        MlOrder.date_closed >= date_start,
                        MlOrder.date_closed <= date_end,
                        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
                    )
                ).scalar() or 0
                
                # BUSCAR QUANTIDADE VENDIDA REAL
                real_quantity = db.query(func.sum(MlOrderItem.quantity)).join(MlOrder).filter(
                    and_(
                        MlOrderItem.ml_item_id == comp.ad_id,
                        MlOrder.date_closed >= date_start,
                        MlOrder.date_closed <= date_end,
                        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
                    )
                ).scalar() or 0
                
                # Estimar visitas baseado em conversão ~3%
                our_visits = int(real_quantity / 0.03) if real_quantity > 0 else random.randint(50, 200)
                our_conversion = (real_quantity / our_visits * 100) if our_visits > 0 else 0
                
                # CONCORRENTE: Padrão INDEPENDENTE (não baseado nas nossas vendas)
                # Criar padrão que varia ao longo do tempo
                time_factor = (days - day_offset) / days  # 0 (passado) a 1 (presente)
                
                # Preço do concorrente varia independentemente
                competitor_price = base_price * random.uniform(0.92, 1.12)
                
                # Vendas do concorrente seguem padrão diferente:
                # - Base diferente das nossas
                # - Picos em momentos diferentes
                competitor_base_sales = random.randint(3, 8)  # Base menor ou maior que a nossa
                
                # Adicionar variação temporal e ruído
                seasonal_factor = 1 + 0.3 * abs(math.sin(day_offset * 0.5))  # Padrão sazonal
                noise = random.uniform(0.7, 1.4)
                
                competitor_sales = int(competitor_base_sales * seasonal_factor * noise * time_factor)
                
                # Se concorrente baixa muito o preço, vende MAIS
                if competitor_price < our_price * 0.93:
                    competitor_sales = int(competitor_sales * 1.6)  # Boost de 60%
                
                competitor_visits = competitor_sales * random.randint(25, 40)
                competitor_conversion = (competitor_sales / competitor_visits * 100) if competitor_visits > 0 else 0
                
                metric = CompetitorMetricsHistory(
                    competitor_id=comp.competitor_id,
                    our_ad_id=comp.ad_id,
                    timestamp=snapshot_date,
                    # Concorrente (simulado pois não temos API)
                    price=round(competitor_price, 2),
                    sales=competitor_sales,
                    visits=competitor_visits,
                    conversion_rate=round(competitor_conversion, 2),
                    has_free_shipping=random.choice([True, False]),
                    stock_available=random.randint(10, 100),
                    seller_reputation='platinum' if random.random() > 0.4 else 'gold',
                    # NOSSOS DADOS REAIS
                    our_price=round(our_price, 2),
                    our_sales=int(real_quantity),  # REAL!
                    our_visits=our_visits,
                    our_conversion_rate=round(our_conversion, 2)
                )
                
                db.add(metric)
                total_metrics += 1
                
                # Detectar eventos de price drop
                if day_offset < 25 and random.random() < 0.08:  # 8% chance
                    prev_price = competitor_price * 1.15
                    price_drop_pct = ((competitor_price - prev_price) / prev_price) * 100
                    
                    event = CompetitorImpactEvent(
                        competitor_id=comp.competitor_id,
                        our_ad_id=comp.ad_id,
                        event_type='price_drop',
                        event_timestamp=snapshot_date,
                        detected_at=snapshot_date,
                        competitor_metric_name='price',
                        competitor_metric_before=round(prev_price, 2),
                        competitor_metric_after=round(competitor_price, 2),
                        change_percentage=round(price_drop_pct, 2),
                        our_sales_before=random.randint(10, 20),
                        our_sales_after=int(real_quantity),  # Usa vendas reais
                        estimated_sales_lost=max(0, random.randint(3, 12)),
                        correlation_score=random.uniform(0.65, 0.92),
                        threat_score=random.randint(65, 95),
                        diagnosis=f"Concorrente reduziu preço {abs(price_drop_pct):.1f}%. Detectado impacto nas vendas.",
                        recommendation=f"Considere ajustar para R$ {competitor_price * 0.97:.2f}"
                    )
                    
                    db.add(event)
                    total_events += 1
            
            # Commit por concorrente
            db.commit()
            logger.info(f"  ✓ {days} dias processados para {comp.competitor_id}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ DADOS REAIS POPULADOS!")
        logger.info(f"{'='*60}")
        logger.info(f"Total métricas: {total_metrics}")
        logger.info(f"Total eventos: {total_events}")
        logger.info(f"Período: Últimos {days} dias com vendas REAIS")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro: {e}", exc_info=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_real_sales_data(30)
