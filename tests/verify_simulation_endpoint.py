import requests
import json
import traceback

def test_simulation():
    # We will test the local functions instead of a live Flask server to avoid needing the web server running
    # Actually, the user asked to verify the endpoint itself. We can use Flask's test client.
    from app.web import app
    
    app.testing = True
    client = app.test_client()
    
    print("--- 1. Caso Base: Panela de Pressão ---")
    payload = {
        "ad_id": "MLB_PANELA",
        "simulate_price": 399.90,
        "target_margin_percent": 19.88,
        "product_cost": {
            "real_cost": 189.38,
            "valor_nf": 94.69,
            "ipi_rate": 7.8,
            "difal_value": 0.0,
            "other_purchase_costs": 0.0,
            "product_origin": "nacional"
        },
        "tax_profile": {
            "full_das_rate": 10.0, # not used since ST is true
            "das_without_icms_rate": 4.83,
            "has_st": True,
            "has_ipi": True,
            "has_difal": False,
            "mva_rate": 72.10,
            "origin_icms_rate": 12.0,
            "destination_icms_rate": 18.0
        },
        "marketplace": {
            "fee_rate": 10.0,
            "fixed_fee": 0.0,
            "freight_cost": 44.05,
            "other_variable_costs": 0.0
        }
    }
    
    # Send request to endpoint (auth is bypassed or we mock it. Wait, the endpoint has @require_auth. We might need a token or we can just mock it.)
    # Since require_auth checks headers, let's just test the logic directly or bypass auth.
    # To be safe, I will mock the require_auth decorator for testing, or just test the logic via a direct call to simulate_pricing if possible.
    # Actually, I'll bypass require_auth by patching it before importing the blueprint, or I'll just write a test token if possible.
    pass

# We will write the test using direct logic to ensure we don't deal with Auth issues
def run_tests():
    from app.services.pricing.types import ProductCostInput, TaxProfileInput, MarketplaceInput
    from app.services.pricing.core_calculator import PricingCoreCalculator
    
    calc = PricingCoreCalculator()
    
    print("--- 1. Caso Base: Panela de Pressão ---")
    pc = ProductCostInput(real_cost=189.38, valor_nf=94.69, ipi_rate=7.8)
    tp = TaxProfileInput(full_das_rate=10.0, das_without_icms_rate=4.83, has_st=True, has_ipi=True, mva_rate=72.10, origin_icms_rate=12.0, destination_icms_rate=18.0)
    mk = MarketplaceInput(selling_price=399.90, fee_rate=10.0, freight_cost=44.05)
    
    res = calc.calculate(pc, tp, mk)
    print(f"IPI: {res.cost_breakdown.ipi_value} (Expected: ~7.39)")
    print(f"ST: {res.cost_breakdown.st_value} (Expected: ~20.26)")
    print(f"Custo Final: {res.cost_breakdown.final_product_cost} (Expected: ~217.03)")
    print(f"DAS: {res.sales_tax_value} (Expected: ~19.32)")
    print(f"Lucro: {res.profit_amount} (Expected: ~79.51)")
    print(f"Margem: {res.contribution_margin_percent}% (Expected: ~19.88%)")
    
    min_zero = calc.find_minimum_price_zero_profit(pc, tp, mk)
    min_target = calc.find_minimum_price_target_margin(pc, tp, mk, 19.88)
    print(f"Min Price Zero Profit: {min_zero}")
    print(f"Min Price Target (19.88%): {min_target}")
    
    print("\n--- 2. Preço Abaixo do Mínimo ---")
    mk2 = MarketplaceInput(selling_price=200.00, fee_rate=10.0, freight_cost=44.05)
    res2 = calc.calculate(pc, tp, mk2)
    print(f"Lucro com R$ 200: {res2.profit_amount}")
    print(f"Status no endpoint seria 'blocked' por ZERO_PROFIT_VIOLATION? {'Sim' if res2.profit_amount < 0 else 'Não'}")
    
    print("\n--- 3. Produto sem ST ---")
    tp3 = TaxProfileInput(full_das_rate=10.0, das_without_icms_rate=4.83, has_st=False, has_ipi=True, mva_rate=0.0, origin_icms_rate=12.0, destination_icms_rate=18.0)
    res3 = calc.calculate(pc, tp3, mk)
    print(f"ST Cobrada: {res3.cost_breakdown.st_value}")
    print(f"DAS Cobrado: {res3.sales_tax_value} (Usou 10% cheio? {'Sim' if res3.sales_tax_value == round(399.90 * 0.1, 2) else 'Não'})")

def test_api():
    from app.web import app
    app.testing = True
    
    # We patch require_auth so we don't need a token
    import app.api.endpoints.auth as auth_mod
    def mock_require_auth(f):
        return f
    # We must patch it before blueprint registration or just bypass it.
    # Actually, the blueprint is already registered in app.web.
    # A simple way to test is to just use app.test_client() but we will get 401.
    # Instead, let's just use the `simulate_pricing` function directly via a mock request context.
    pass

def test_api_direct():
    from app.web import app
    from app.api.endpoints.pricing import simulate_pricing
    
    with app.test_request_context(json={
        "ad_id": "MLB_PANELA",
        "simulate_price": 399.90,
        "target_margin_percent": 19.88,
        "product_cost": {
            "real_cost": 189.38,
            "valor_nf": 94.69,
            "ipi_rate": 7.8,
            "difal_value": 0.0,
            "other_purchase_costs": 0.0,
            "product_origin": "nacional"
        },
        "tax_profile": {
            "full_das_rate": 10.0,
            "das_without_icms_rate": 4.83,
            "has_st": True,
            "has_ipi": True,
            "has_difal": False,
            "mva_rate": 72.10,
            "origin_icms_rate": 12.0,
            "destination_icms_rate": 18.0
        },
        "marketplace": {
            "fee_rate": 10.0,
            "fixed_fee": 0.0,
            "freight_cost": 44.05,
            "other_variable_costs": 0.0
        }
    }):
        res = simulate_pricing()
        print("\n--- TESTE ENDPOINT /api/pricing/simulate ---")
        import json
        print(json.dumps(res.get_json(), indent=2))

    print("\n--- TESTE ENDPOINT FALTA DE DADOS ---")
    with app.test_request_context(json={
        "ad_id": "MLB_FAIL",
        "simulate_price": 399.90,
        "target_margin_percent": 19.88,
        "product_cost": {
            "real_cost": 189.38
        },
        "tax_profile": {},
        "marketplace": {}
    }):
        res2, code = simulate_pricing()
        print(f"Status Code: {code}")
        print(json.dumps(res2.get_json(), indent=2))

if __name__ == '__main__':
    run_tests()
    test_api_direct()
