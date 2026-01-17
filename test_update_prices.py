
from app.core.database import SessionLocal
from app.services.competition_engine import CompetitionEngine
import logging

# Configure logging to see Scraper output
logging.basicConfig(level=logging.INFO)

def test_update():
    db = SessionLocal()
    try:
        engine = CompetitionEngine(db)
        
        # We need an Ad ID and a Competitor linked to it to test.
        # Let's see if we have one or create a dummy one.
        # Ideally we use the one created in previous test if it exists.
        
        # Hardcode a known Ad ID from previous steps or just find one
        from app.models.ad import Ad
        ad = db.query(Ad).first()
        if not ad:
            print("No Ad found")
            return

        print(f"Using Ad {ad.id}")
        
        # Ensure we have a competitor with the user's URL
        url = "https://produto.mercadolivre.com.br/MLB-4200110239-bar-cooler-inflavel-flutuante-intex-piscina-24-latas-boia-_JM"
        print(f"Adding/Getting competitor {url}...")
        comp = engine.add_competitor(ad.id, url)
        print(f"Competitor ID: {comp.id}, Current Price: {comp.price}")
        
        print("Running Update...")
        count = engine.update_competitor_prices(ad.id)
        print(f"Updated {count} competitors")
        
        # Re-fetch
        db.refresh(comp)
        print(f"New Price: {comp.price}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_update()
