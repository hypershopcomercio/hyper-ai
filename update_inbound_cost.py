
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

def update_cost():
    db = SessionLocal()
    try:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == 'avg_inbound_cost').first()
        if cfg:
            print(f"Updating avg_inbound_cost from {cfg.value} to 0.85")
            cfg.value = '0.85'
            db.commit()
        else:
            print("Config key not found.")
    finally:
        db.close()

if __name__ == "__main__":
    update_cost()
