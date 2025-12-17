
import os
from dotenv import load_dotenv

def debug_env():
    print("--- Reading .env file raw content ---")
    try:
        with open(".env", "r") as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading .env: {e}")
    
    print("\n--- Checking os.environ after load_dotenv ---")
    load_dotenv()
    db_url = os.environ.get("DATABASE_URL")
    print(f"DATABASE_URL: {db_url}")

if __name__ == "__main__":
    debug_env()
