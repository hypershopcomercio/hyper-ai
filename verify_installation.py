
import sys
import os

# Ensure root is in path
sys.path.append(os.getcwd())

print("Attempting to import app.web...")
try:
    from app.web import app
    print("VERIFICATION_SUCCESS: App imported successfully.")
except Exception as e:
    print("VERIFICATION_FAILED")
    import traceback
    traceback.print_exc()
