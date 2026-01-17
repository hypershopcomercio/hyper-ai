
import logging
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
import json

logging.basicConfig(level=logging.INFO)

def inspect_item():
    db = SessionLocal()
    service = MeliApiService(db)
    
    item_id = "MLB3862661909"
    print(f"Fetching details for {item_id}...")
    
    try:
        # Get full details (Must pass LIST)
        data = service.get_item_details([item_id])
        
        if isinstance(data, list):
            data = data[0]
            
        # Save to file for full inspection if needed
        with open("debug_item_full.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print("Data saved to debug_item_full.json")
        
        # Immediate check
        print(f"Video ID: {data.get('video_id')}")
        print(f"Short Desc: {data.get('short_description')}")
        
        # Check specific attributes
        attrs = data.get('attributes', [])
        video_attrs = [a for a in attrs if 'VIDEO' in a.get('id', '').upper() or 'CLIP' in a.get('id', '').upper()]
        print(f"Video Attributes: {video_attrs}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_item()
