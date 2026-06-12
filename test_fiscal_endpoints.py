import os
from dotenv import load_dotenv
load_dotenv(override=True)

from app.web import app
from app.core.database import SessionLocal
from app.models.token import Token
from app.models.ad import Ad
import json

# 1. Obter um Token Válido e um Ad Real
db = SessionLocal()
token_obj = db.query(Token).first()
if not token_obj:
    print("Nenhum token encontrado no banco de dados!")
    exit(1)

token = token_obj.access_token

ad_obj = db.query(Ad).first()
if not ad_obj:
    print("Nenhum anúncio encontrado no banco de dados!")
    exit(1)

ad_id = ad_obj.id
db.close()

print(f"Usando Token: {token[:10]}...")
print(f"Usando Ad ID: {ad_id}")

client = app.test_client()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

def print_res(res):
    print(f"Status: {res.status_code}")
    print(json.dumps(res.get_json(), indent=2))
    print("-" * 40)

print("\n--- TESTE SEM TOKEN (Esperado 401) ---")
res = client.get("/api/finance/tax-configs")
print_res(res)

print("\n--- TESTE 1: GET /api/finance/tax-configs ---")
res = client.get("/api/finance/tax-configs", headers=headers)
print_res(res)

print("\n--- TESTE 2: POST /api/finance/tax-configs ---")
payload = {
  "reference_month": "2026-06",
  "full_das_rate": 10.0,
  "das_without_icms_rate": 4.83,
  "notes": "Teste Automatizado",
  "is_active": True
}
res = client.post("/api/finance/tax-configs", headers=headers, json=payload)
print_res(res)

print(f"\n--- TESTE 3: GET /api/ads/{ad_id}/fiscal-profile ---")
res = client.get(f"/api/ads/{ad_id}/fiscal-profile", headers=headers)
print_res(res)

print(f"\n--- TESTE 4: PUT /api/ads/{ad_id}/fiscal-profile ---")
payload_put = {
  "tax_profile": {
    "sku": "SKU-EXEMPLO-123",
    "product_origin": "nacional",
    "origin_uf": "SC",
    "destination_uf_default": "SP",
    "has_st": True,
    "has_ipi": True,
    "mva_rate": 72.10,
    "ipi_rate": 7.8,
    "origin_icms_rate": 12.0,
    "destination_icms_rate": 18.0
  },
  "purchase_cost": {
    "sku": "SKU-EXEMPLO-123",
    "real_cost": 189.38,
    "nf_value": 94.69
  }
}
res = client.put(f"/api/ads/{ad_id}/fiscal-profile", headers=headers, json=payload_put)
print_res(res)

print(f"\n--- TESTE 5: GET /api/ads/{ad_id}/fiscal-profile (Persistência) ---")
res = client.get(f"/api/ads/{ad_id}/fiscal-profile", headers=headers)
print_res(res)
