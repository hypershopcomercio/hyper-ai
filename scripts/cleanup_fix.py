import sys
import os
import re
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, r'C:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data')

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig, ForecastLog

def run_cleanup():
    db = SessionLocal()
    try:
        print("--- Starting Cleanup ---")
        
        # 1. Clean Bad Momentum Keys (Numeric keys like '0.7', '1.0')
        print("\n1. Cleaning Bad Momentum Keys...")
        bad_configs = db.query(MultiplierConfig).filter(
            MultiplierConfig.tipo == 'momentum'
        ).all()
        
        deleted_count = 0
        for config in bad_configs:
            # Check if key looks like a float (e.g., '0.7', '1.0', '0.818')
            # Valid keys are 'alto', 'baixo', 'muito_alto', etc.
            if re.match(r'^\d+(\.\d+)?$', config.chave):
                print(f"   Deleting bad key: {config.tipo}.{config.chave} (Value: {config.valor})")
                db.delete(config)
                deleted_count += 1
        
        if deleted_count > 0:
            db.commit()
            print(f"   ✓ Deleted {deleted_count} bad momentum keys.")
        else:
            print("   ✓ No bad momentum keys found.")

        # 2. Remove 'Kit 2 Cooler' from recent logs (last 48h)
        print("\n2. Removing 'Kit 2 Cooler' from recent logs...")
        two_days_ago = datetime.now() - timedelta(days=2)
        recent_logs = db.query(ForecastLog).filter(
            ForecastLog.timestamp_previsao >= two_days_ago
        ).all()
        
        updated_logs = 0
        for log in recent_logs:
            if not log.fatores_usados:
                continue
                
            product_mix = log.fatores_usados.get('_product_mix', [])
            if not product_mix:
                continue
                
            # Filter out the specific product
            # Match by title part "Kit 2 Cooler Flutuante"
            new_mix = [
                p for p in product_mix 
                if "Kit 2 Cooler Flutuante" not in p.get('title', '')
            ]
            
            if len(new_mix) < len(product_mix):
                print(f"   Log #{log.id}: Removed {len(product_mix) - len(new_mix)} items matching 'Kit 2 Cooler'")
                
                # Careful: modifying JSONB in SQLAlchemy requires reassignment to trigger update
                fatores = dict(log.fatores_usados) # shallow copy
                fatores['_product_mix'] = new_mix
                log.fatores_usados = fatores
                updated_logs += 1
        
        if updated_logs > 0:
            db.commit()
            print(f"   ✓ Updated {updated_logs} logs.")
        else:
            print("   ✓ No logs needed 'Kit 2 Cooler' removal.")

        print("\n--- Cleanup Complete ---")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_cleanup()
