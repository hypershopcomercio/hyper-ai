
import sys
import os
import logging

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.health_engine import HealthEngine

# Config
ITEM_ID = "MLB3964133363"

def test_health():
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ITEM_ID).first()
        if not ad:
            print("Ad not found")
            return

        engine = HealthEngine()
        result = engine.analyze(ad)
        
        print(f"--- HEALTH ANALYSIS FOR {ad.id} ---")
        print(f"Score: {result['score']}")
        print(f"Status: {result['status']}")
        print(f"Label: {result['label']}")
        print("\n--- ISSUES ---")
        for issue in result['all_issues']:
            print(f"- {issue}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_health()
