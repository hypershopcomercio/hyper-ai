
from app.core.database import engine, Base
from app.models.ad_variation import AdVariation
from app.models.ad import Ad # Ensure Ad is loaded

def migrate():
    print("Creating ad_variations table...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    migrate()
