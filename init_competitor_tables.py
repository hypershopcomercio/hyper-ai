
from app.core.database import engine
from app.models.base import Base
from app.models.competitor_ad import CompetitorAd
from app.models.ad_keyword import AdKeyword

def init_tables():
    print("Creating tables for Competition Engine...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_tables()
