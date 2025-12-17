
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.meli_sync import MeliSyncService

def check_variations():
    db = SessionLocal()
    try:
        # Find an ad without SKU
        ad = db.query(Ad).filter(Ad.sku == None).first()
        if not ad:
            print("No ads without SKU found to check.")
            return

        print(f"Checking Ad: {ad.id} - {ad.title}")
        
        # Fetch directly from ML
        service = MeliSyncService()
        try:
            token = service.auth.get_valid_token()
            import requests
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"https://api.mercadolibre.com/items/{ad.id}", headers=headers)
            if res.status_code == 200:
                data = res.json()
                variations = data.get("variations", [])
                print(f"Has Variations: {len(variations) > 0}")
                if variations:
                    print(f"Variation Count: {len(variations)}")
                    for v in variations:
                        # Try to find SKU in variation
                        v_sku = None
                        if v.get("seller_custom_field"):
                            v_sku = v.get("seller_custom_field")
                        else:
                            for attr in v.get("attributes", []):
                                if attr["id"] == "SELLER_SKU":
                                    v_sku = attr["value_name"]
                        print(f" - Var ID: {v['id']} | SKU: {v_sku}")
            else:
                print(f"Failed to fetch ML data: {res.status_code}")
        except Exception as ex:
            print(f"Error fetching ML: {ex}")

    finally:
        db.close()

if __name__ == "__main__":
    check_variations()
