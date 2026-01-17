
import requests
import logging
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO)

def check_clips_endpoint():
    db = SessionLocal()
    service = MeliApiService(db)
    
    item_id = "MLB3964133363"
    print(f"Checking Clips for {item_id}...")
    
    # Try conceptual endpoints
    endpoints = [
        f"/items/{item_id}/clips",
        f"/clips/search?item_id={item_id}",
        f"/items/{item_id}?include_attributes=all" 
    ]
    
    for ep in endpoints:
        print(f"  Probing {ep}...")
        try:
            # We use service.request manually to handle custom paths if needed, 
            # but service.request assumes base_url.
            # Let's use service.request
            # MeliApiService.request(method, endpoint, ...)
            
            # Check if request method is available and public/private
            # Assuming GET
            try:
                # MeliApiService might not expose generic request publically easily if I didn't verify code.
                # Inspecting code: yes it has `request` method.
                data = service.request("GET", ep)
                print(f"  [SUCCESS] {ep}: {str(data)[:200]}") # Print start of response
            except Exception as e:
                print(f"  [FAILED] {ep}: {e}")
                
        except Exception as outer_e:
            print(f"  Outer Error: {outer_e}")

if __name__ == "__main__":
    check_clips_endpoint()
