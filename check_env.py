
from dotenv import load_dotenv
import os

load_dotenv()

keys = ["MELI_APP_ID", "MELI_CLIENT_SECRET", "MELI_REDIRECT_URI", "TINY_API_TOKEN", "MELI_USER_ID"]
print("Checking .env config:")
for k in keys:
    val = os.getenv(k)
    if not val:
        print(f"[MISSING] {k}")
    elif "your_" in val.lower() or "replace" in val.lower():
        print(f"[PLACEHOLDER] {k} appears to be a placeholder: '{val}'")
    else:
        # Show first/last chars to confirm it's not empty/whitespace
        masked = f"{val[:2]}...{val[-2:]}" if len(val) > 4 else "****"
        print(f"[OK] {k} is present ({masked})")
