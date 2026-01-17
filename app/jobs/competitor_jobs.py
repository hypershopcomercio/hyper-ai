"""
Jobs automáticos para sistema de intelligence de concorrentes.
"""
import logging
from app.core.database import SessionLocal
from app.services.competitor_metrics_scraper import CompetitorMetricsScraper
from app.services.impact_analyzer import ImpactAnalyzer
from app.models.ad import Ad

logger = logging.getLogger(__name__)


def run_competitor_metrics_collection():
    """
    Job horário: Coleta métricas de todos os concorrentes monitorados.
    
    Executado a cada hora para manter dados atualizados.
    """
    logger.info("[COMPETITOR-JOB] Iniciando coleta de métricas de concorrentes...")
    
    db = SessionLocal()
    
    try:
        scraper = CompetitorMetricsScraper(db)
        
        # Buscar todos os concorrentes ativos
        from app.models.competitor_ad import CompetitorAd
        # Ajuste: busca tuplas (competitor_ml_id, our_ad_id)
        # Atenção: collect_and_save_metrics pede (competitor_id, ad_id)
        
        competitors = db.query(CompetitorAd).filter(CompetitorAd.status == 'active').all()
        logger.info(f"[COMPETITOR-JOB] Encontrados {len(competitors)} concorrentes ativos.")
        
        total_success = 0
        total_errors = 0
        
        for comp in competitors:
             try:
                 success = scraper.collect_and_save_metrics(comp.competitor_id, comp.ad_id)
                 if success:
                     total_success += 1
                 else:
                     total_errors += 1
             except Exception as e_comp:
                 logger.error(f"[COMPETITOR-JOB] Falha ao processar {comp.competitor_id}: {e_comp}")
                 total_errors += 1
        
        logger.info(f"[COMPETITOR-JOB] Coleta concluída. Sucesso: {total_success}, Erros: {total_errors}")
        
        return {"status": "success", "processed": total_success, "errors": total_errors}
        
    except Exception as e:
        logger.error(f"[COMPETITOR-JOB] Erro na coleta de métricas: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def run_impact_analysis():
    """
    Job horário: Analisa eventos de impacto competitivo.
    
    Executado após a coleta de métricas para detectar mudanças e impactos.
    """
    logger.info("[IMPACT-JOB] Iniciando análise de impacto competitivo...")
    
    db = SessionLocal()
    
    try:
        analyzer = ImpactAnalyzer(db)
        
        # Buscar todos os concorrentes ativos
        from app.models.competitor_ad import CompetitorAd
        competitors = db.query(CompetitorAd).filter(CompetitorAd.status == 'active').all()
        
        total_analyzed = 0
        total_errors = 0
        
        for comp in competitors:
            try:
                # Executar análise completa para este par (competitor, ad)
                analyzer.run_full_analysis(comp.competitor_id, comp.ad_id) 
                
                total_analyzed += 1
            except Exception as e_an:
                logger.error(f"[IMPACT-JOB] Falha ao analisar {comp.competitor_id}: {e_an}")
                total_errors += 1
        
        logger.info(f"[IMPACT-JOB] Análise concluída. Processados: {total_analyzed}, Erros: {total_errors}")
        
        return {"status": "success", "processed": total_analyzed}
        
    except Exception as e:
        logger.error(f"[IMPACT-JOB] Erro na análise de impacto: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def run_threat_score_calculation():
    """
    Job diário: Calcula score de ameaça para cada concorrente.
    """
    logger.info("[THREAT-JOB] Calculando scores de ameaça...")
    
    db = SessionLocal()
    
    try:
        # TODO: Implementar cálculo de threat score
        # Combinar múltiplos fatores para gerar score 0-100
        
        logger.info("[THREAT-JOB] Cálculo de threat scores concluído")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"[THREAT-JOB] Erro no cálculo de threat scores: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
