import logging
import time
from app.services.sync_engine import SyncEngine

logger = logging.getLogger(__name__)

def run_daily_sync():
    logger.info("Scheduler: Starting Daily Sync Job...")
    engine = SyncEngine()
    
    # 1. Sync Ads (Metadata, Status, Price)
    engine.sync_ads()
    
    # 2. Sync Ads Metrics (Cost, Clicks, etc)
    # Added via user request to avoid API latency during dashboard load
    if hasattr(engine, 'sync_ads_metrics'):
        engine.sync_ads_metrics()

    # 2b. Sync REAL per-item daily Ads metrics (ml_ads_item_daily)
    # Source of truth for per-sale Ads attribution
    if hasattr(engine, 'sync_ads_item_daily'):
        engine.sync_ads_item_daily(days_back=3)
        
    # 3. Sync Metrics (Visits, Sales, Conversion)
    engine.sync_metrics()
    run_financial_metrics_calculation()

    # 3b. Sync estoque no Full + custo real de armazenagem (alimenta o financeiro)
    run_full_sync()

    # 4. Motor de decisão de Ads: gera recomendações, mede outcomes e notifica
    run_ads_decision_engine()

    logger.info("Scheduler: Daily Sync Job Finished.")


def run_financial_metrics_calculation():
    """Refresh fixed-cost allocation after the daily order synchronization."""
    from app.core.database import SessionLocal
    from app.services.financial_service import FinancialService

    db = SessionLocal()
    try:
        summary = FinancialService(db).calculate_metrics()
        logger.info(
            "Financial metrics sync completed: %s SKUs, R$ %.2f allocated.",
            summary["skus_processed"],
            summary["fixed_cost_allocated_30d"],
        )
        return summary
    except Exception:
        db.rollback()
        logger.exception("Financial metrics sync failed.")
        raise
    finally:
        db.close()


def run_full_sync():
    """Sincroniza estoque no Full e recalcula custo real de armazenagem/inbound."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        from app.services.full_service import FullService
        svc = FullService(db=db)
        result = svc.sync_and_cost()
        logger.info(f"Full sync: {result}")
    except Exception as e:
        logger.error(f"Full sync job failed: {e}")
        db.rollback()
    finally:
        db.close()


def run_ads_decision_engine():
    """Gera recomendações de Ads + feedback loop + notificação WhatsApp (se configurada)."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        from app.services.ads_decision_engine import AdsDecisionEngine
        engine = AdsDecisionEngine(db)

        summary = engine.generate_recommendations(days=30)
        engine.measure_outcomes()

        if summary.get("created"):
            from app.services.notifier import send_whatsapp, format_ads_recommendations_summary
            send_whatsapp(format_ads_recommendations_summary(summary))
    except Exception as e:
        logger.error(f"Ads Decision Engine job failed: {e}")
        db.rollback()
    finally:
        db.close()
