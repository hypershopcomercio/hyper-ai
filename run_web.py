import os
from dotenv import load_dotenv

# Force reload environment variables from .env file, overriding any stale shell envs
load_dotenv(override=True)

print(f"DEBUG PRE-IMPORT: DATABASE_URL={os.getenv('DATABASE_URL')}")

from app.web import app

if __name__ == "__main__":
    print("Starting Hyper Sync Web Server...")
    # Enable CORS for development (allowing frontend localhost:3000)
    from flask_cors import CORS
    CORS(app) 
    app.run(host="0.0.0.0", port=5000, debug=True)
