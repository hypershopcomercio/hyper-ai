
import requests
import json
from app.core.database import SessionLocal
from app.models.ad import Ad

# Config
API_URL = "http://localhost:5000/api" # Adjust port if needed, usually 5000 or 8000. 
# Wait, this environment doesn't have the server running on localhost accessible via requests if I don't start it.
# Usually I test by invoking the app or service directly in python script, not via HTTP requests unless I start the server in background.

# Better approach: Test the SERVICE directly.
# And test the FLASK ROUTE via test_client.

# from app.main import app 


from app.services.competition_engine import CompetitionEngine

def test_service_directly():
    print("Testing Service Directly...")
    db = SessionLocal()
    try:
        # 1. Get an Ad
        ad = db.query(Ad).first()
        if not ad:
            print("No ads found to test.")
            return

        print(f"Using Ad: {ad.id} - {ad.title}")
        
        # 2. Add Competitor (using a known safe ID or just an ID format)
        # Note: This will try to hit MELI API.
        # Let's use a very common item or just a random ID and expect failure if API is blocked,
        # but we want to test the logic.
        
        # Example URL from a known competitor (or just made up MLB ID)
        # MLB1234567890
        test_url = "https://produto.mercadolivre.com.br/MLB-1234567890-produto-teste-_JM"
        
        engine = CompetitionEngine(db)
        
        print(f"Adding competitor {test_url}...")
        try:
            comp = engine.add_competitor(ad.id, test_url)
            print(f"Success! Added {comp.id} - {comp.title}")
        except Exception as e:
            print(f"Expected error (if API blocked) or real error: {e}")

        # 3. List
        competitors = engine.get_competitors(ad.id)
        print(f"Competitors found: {len(competitors)}")
        for c in competitors:
            print(f" - {c.id}: {c.title} ({c.price})")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_service_directly()
