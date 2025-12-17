
import os
from dotenv import load_dotenv
import urllib.parse

# Force load
load_dotenv(override=True)

APP_ID = os.getenv("MELI_APP_ID")
REDIRECT_URI = os.getenv("MELI_REDIRECT_URI")

print(f"DEBUG: APP_ID='{APP_ID}'")
print(f"DEBUG: REDIRECT_URI='{REDIRECT_URI}'")

base_url = "https://auth.mercadolivre.com.br/authorization"
params = {
    "response_type": "code",
    "client_id": APP_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": "read:items write:items offline_access read:orders"
}
url = f"{base_url}?{urllib.parse.urlencode(params)}"
print(f"DEBUG: Generated URL: {url}")
