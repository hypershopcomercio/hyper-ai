
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal

# A random Ad ID likely not owned by the user (competitor)
# Searching for a real ID example from previous logs or generic knowledge?
# Let's use a very old/common ID if possible, or one from the search (oh wait search failed).
# I will try to find a valid MLB ID from the user's current ads, and just assume asking for *another* ID works the same if it's public.
# Actually, calling public items updates is usually allowed. 
# Let's try to fetch details for a known item. 
# I'll use the user's own item first to verify the script, then I'll try to find a competitor.
# Since I can't search, I'll trust the user to provide one eventually. 
# But to test "Monitoring" I need to be sure `get_items` works for *public* non-owned items.
# I'll assume it does because it's the standard API behavior.
# I will try to fetch checking if `get_items` fails for unowned items with the current token.
# I'll use a hardcoded ID that is likely valid. 
# SInce I don't have one, I will try to fetch the user's own ID but treat it as a "check".
# Wait, I can try to fetch a variation of an ID or a random one? No, bad idea.
# I will assume success for now, but I'll write the script to test the User's Own ID first to ensure the library works.
# Actually, I'll assume the library works (it's used in sync).
# I will proceed to tell the user about the Search block and propose the "Link Paste" method.

# BUT, to be sure, I will write a script that tries to access the public `items/{id}` endpoint without a token, or with the user token.
# If `items/{id}` is 403 for non-owned items, then we are dead.
# Let's probe `check_item_access.py` with a knwon valid MLB from the user list, but try to access it anonymously to simulate "public access".

import requests
import json

ID_TO_CHECK = "MLB5313761220" # The user's own item, but let's check public access

def check_public_item(item_id):
    base_url = "https://api.mercadolibre.com"
    endpoint = f"/items/{item_id}"
    print(f"--- CHECKING PUBLIC ITEM: {item_id} ---")
    
    # 1. Anonymous
    try:
        resp = requests.get(f"{base_url}{endpoint}")
        print(f"Anonymous Status: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS: Public Access OK")
            print(resp.json().get("title"))
        else:
            print(f"Anonymous Error: {resp.status_code}")
    except Exception as e:
        print(f"Exc: {e}")

if __name__ == "__main__":
    check_public_item(ID_TO_CHECK)
