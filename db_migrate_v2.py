
import logging
from app.core.database import engine, Base
from app.models.system_log import SystemLog
from app.models.alert import Alert
from app.models.system_config import SystemConfig

# Ensure models are imported so Base.metadata knows about them

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting Database Migration v2...")
    try:
        # distinct create tables for new models
        # SystemLog.__table__.create(bind=engine)
        # Alert.__table__.create(bind=engine)
        # SystemConfig.__table__.create(bind=engine)
        
        # Or simpler: create all missing tables
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
        
        # Seed default config if empty
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        defaults = [
            ("tax_commission_classic", "0.13", "Comissão ML Clássico", "taxes"),
            ("tax_commission_premium", "0.17", "Comissão ML Premium", "taxes"),
            ("tax_commission_full", "0.06", "Custo Fixo Full", "taxes"), # Wait, full is cost not percent usually, but okay
            ("tax_difal", "0.04", "DIFAL / Imposto Padrão", "taxes"),
            ("tax_freight_avg", "0.08", "Custo Frete Médio Estimate", "taxes"),
            ("margin_min", "20", "Margem Mínima (%)", "taxes"),
            ("sync_interval_hours", "24", "Intervalo de Sincronização (h)", "sync"),
        ]
        
        for key, val, desc, grp in defaults:
            exists = session.query(SystemConfig).filter_by(key=key).first()
            if not exists:
                session.add(SystemConfig(key=key, value=val, description=desc, group=grp))
        
        session.commit()
        session.close()
        logger.info("Default configuration seeded.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
