
from app.core.database import Base, engine
from app.models.oauth_token import OAuthToken
import logging

logging.basicConfig(level=logging.INFO)

def run():
    logging.info("Creating oauth_tokens table...")
    Base.metadata.create_all(bind=engine)
    logging.info("Done.")

if __name__ == "__main__":
    run()
