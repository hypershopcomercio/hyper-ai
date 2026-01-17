
import sys
import os
import logging
import requests
import json
from datetime import datetime

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.meli_api import MeliApiService

logging.basicConfig(level=logging.INFO)

TARGET_VALUES = [142, 8, 150]
TARGET_ID = "MLB3964133363"

def find_values(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_values(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_values(v, f"{path}[{i}]")
    elif isinstance(obj, (int, float)):
        if int(obj) in TARGET_VALUES:
            print(f"!!! FOUND MATCH !!! Value: {obj} at Path: {path}")

def scan_for_values():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        # 1. Get Seller ID
        me_res = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
        seller_id = me_res.json()["id"]
        print(f"Seller ID: {seller_id}")
        
        # 2. Get Item & Inventory ID
        item_res = requests.get(f"https://api.mercadolibre.com/items/{TARGET_ID}?include_attributes=all", headers=headers)
        item_data = item_res.json()
        inventory_id = item_data.get('inventory_id')
        print(f"Inventory ID: {inventory_id}")

        endpoints = [
            # Inbound Shipments (Broad search)
            f"https://api.mercadolibre.com/inbound/shipments/search?seller_id={seller_id}&status=shipped,closed,delivered,created,ready_to_ship",
            f"https://api.mercadolibre.com/inbound/shipments/search?seller_id={seller_id}",
            
            # Stock Operations
            f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}",
            f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}&filters=inventory_id:{inventory_id}" if inventory_id else None,
            
            # Item Stock (specific)
            f"https://api.mercadolibre.com/inventory/items/{inventory_id}" if inventory_id else None,
            
            # Additional Probes
            f"https://api.mercadolibre.com/items/{TARGET_ID}/stock/fulfillment", # Hypothetical
            f"https://api.mercadolibre.com/users/{seller_id}/brands", # Testing auth scope
        ]

        for url in endpoints:
            if not url: continue
            print(f"\n--- SCANNING {url} ---")
            res = requests.get(url, headers=headers)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                find_values(data, url)
            else:
                print(f"Error: {res.text[:200]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    scan_for_values()
