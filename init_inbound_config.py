
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

def init_config():
    db = SessionLocal()
    try:
        print("--- INITIALIZING INBOUND CONFIG ---")
        
        # Check if exists
        cfg = db.query(SystemConfig).filter(SystemConfig.key == 'avg_inbound_cost').first()
        if not cfg:
            print("Creating 'avg_inbound_cost' = 0.00")
            new_cfg = SystemConfig(
                key='avg_inbound_cost',
                value='0.00',
                description='Custo médio de envio Full por unidade (R$)',
                group='logistics'
            )
            db.add(new_cfg)
        else:
            print(f"Config exists: {cfg.value}")
            # Optional: Update description if needed
            cfg.description = 'Custo médio de envio Full por unidade (R$)'
            cfg.group = 'logistics'
        
        db.commit()
        print("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    init_config()
