import sys
import os
import json

# Add the project root to sys.path
sys.path.append(r"c:\Users\Michel\Documents\hyper-ai")

# Force load dotenv BEFORE importing anything from app
from dotenv import load_dotenv
load_dotenv(os.path.join(r"c:\Users\Michel\Documents\hyper-ai", ".env"))

from app.core.database import SessionLocal
from app.services.pricing.resolver import PricingDataResolver

def test_resolver():
    db = SessionLocal()
    try:
        resolver = PricingDataResolver(db)
        result = resolver.resolve("MLB6232864820")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        db.close()

if __name__ == "__main__":
    test_resolver()
