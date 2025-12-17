
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

def init_settings():
    db = SessionLocal()
    try:
        # Check taxes
        tax = db.query(SystemConfig).filter(SystemConfig.key == "tax_das_percent").first()
        if not tax:
            print("Creating default tax_das_percent = 0.0")
            tax = SystemConfig(key="tax_das_percent", value="0.0", description="Imposto DAS Simples Nacional (%)", group="taxes")
            db.add(tax)
        else:
            print(f"Tax exists: {tax.value}%")
            
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_settings()
