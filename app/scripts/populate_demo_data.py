"""
Popular dados históricos SIMULADOS para demonstração do sistema.
Usa dados reais dos concorrentes cadastrados + variações realistas.
"""
import logging
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.competitor_ad import CompetitorAd
from app.models.competitor_intelligence import CompetitorMetricsHistory, CompetitorImpactEvent
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_demo_data(days=90):
    db = SessionLocal()
    try:
        competitors = db.query(CompetitorAd).all()
        logger.info(f"Encontrados {len(competitors)} concorrentes")
        
        if not competitors:
            logger.error("Nenhum concorrente cadastrado!")
            return
        
        total_metrics = 0
        total_events = 0
        
        for comp in competitors:
            logger.info(f"Processando: {comp.competitor_id}")
            
            # Preço base (atual com pequenas variações)
            base_price = comp.price if comp.price else 150.0
            
            # Criar 90 snapshots diários
            for day_offset in range(days, 0, -1):
                snapshot_date = datetime.utcnow() - timedelta(days=day_offset)
                
                # Simular variação realista de preço
                if day_offset > 60:
                    # Período antigo: preços mais altos
                    daily_price = base_price * random.uniform(1.05, 1.15)
                elif day_offset > 30:
                    # Período médio: redução gradual
                    daily_price = base_price * random.uniform(0.98, 1.08)
                else:
                    # Período recente: preços próximos ao atual
                    daily_price = base_price * random.uniform(0.95, 1.02)
                
                # Simular vendas acumuladas (crescem ao longo do tempo)
                daily_sales = max(0, int((90 - day_offset) * random.uniform(0.5, 1.5)))
                
                # Simular NOSSAS vendas (inversamente proporcional ao preço deles)
                # Quando eles baixam preço, perdemos vendas
                our_price_base = base_price * 0.95  # Nosso preço base um pouco mais baixo
                our_daily_sales = max(0, int((90 - day_offset) * random.uniform(0.8, 2.0)))
                
                # Se concorrente está muito barato, perdemos mais vendas
                if daily_price < our_price_base * 0.9:
                    our_daily_sales = int(our_daily_sales * 0.6)  # Perda de 40%
                
                metric = CompetitorMetricsHistory(
                    competitor_id=comp.competitor_id,
                    our_ad_id=comp.ad_id,
                    timestamp=snapshot_date,
                    # Dados do concorrente
                    price=round(daily_price, 2),
                    sales=daily_sales,
                    visits=daily_sales * random.randint(15, 35),  # Taxa conversão ~3%
                    conversion_rate=random.uniform(2.5, 4.5),
                    has_free_shipping=random.choice([True, False]),
                    stock_available=random.randint(5, 100),
                    seller_reputation='platinum' if random.random() > 0.3 else 'gold',
                    # NOSSOS DADOS
                    our_price=round(our_price_base, 2),
                    our_sales=our_daily_sales,
                    our_visits=our_daily_sales * random.randint(20, 40),
                    our_conversion_rate=random.uniform(3.0, 5.0)
                )
                
                db.add(metric)
                total_metrics += 1
                
                # Criar evento de impacto esporádico (price drop significativo)
                if random.random() < 0.05 and day_offset < 60:  # 5% chance nos últimos 60 dias
                    prev_price = base_price * 1.1  # Preço anterior mais alto
                    price_change_pct = ((daily_price - prev_price) / prev_price) * 100
                    
                    event = CompetitorImpactEvent(
                        competitor_id=comp.competitor_id,
                        our_ad_id=comp.ad_id,
                        event_type='price_drop',
                        event_timestamp=snapshot_date,
                        detected_at=snapshot_date,
                        competitor_metric_name='price',
                        competitor_metric_before=round(prev_price, 2),
                        competitor_metric_after=round(daily_price, 2),
                        change_percentage=round(price_change_pct, 2),
                        our_sales_before=random.randint(8, 15),
                        our_sales_after=random.randint(3, 8),
                        estimated_sales_lost=random.randint(5, 20),
                        correlation_score=random.uniform(0.6, 0.9),
                        threat_score=random.randint(60, 95),
                        diagnosis=f"Concorrente reduziu preço em {abs(price_change_pct):.1f}%. Estimado perda de {random.randint(5,20)} vendas.",
                        recommendation=f"Considere ajustar para R$ {daily_price - 5:.2f} para manter competitividade."
                    )
                    
                    db.add(event)
                    total_events += 1
            
            # Commit a cada concorrente
            db.commit()
            logger.info(f"  ✓ {90} métricas + eventos criados para {comp.competitor_id}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ DEMO DATA POPULADO COM SUCESSO!")
        logger.info(f"{'='*60}")
        logger.info(f"Total métricas: {total_metrics}")
        logger.info(f"Total eventos: {total_events}")
        logger.info(f"Cobertura: {days} dias para {len(competitors)} concorrentes")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_demo_data(90)
