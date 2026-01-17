import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.pricing_engine import PricingEngine
from app.models.ad import Ad

# Mock classes
class MockQuery:
    def __init__(self, data):
        self.data = data
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return self.data[0] if self.data else None

class MockDB:
    def __init__(self, ad_data=None):
        self.ad_data = ad_data
    def query(self, *args):
        return MockQuery([self.ad_data] if self.ad_data else [])

def test_fixed_pricing_logic():
    print(">>> Testing Fixed Pricing Logic (R$ 0.40/day)...")
    
    # 1. Setup
    current_price = 100.00
    target_price = 102.00 # Increase of 2.00 -> Should be exactly 5 steps (2.00 / 0.40 = 5)
    
    # Mock Ad is irrelevant for this specific method as it uses args mostly, 
    # but elasticity calculation needs it.
    # We will mock elasticity to return None (default path in old logic) or just ignore it 
    # because NEW logic overrides elasticity.
    
    engine = PricingEngine(MockDB())
    
    # Monkeypatch calculate_elasticity to avoid DB lookup
    engine.calculate_elasticity = lambda item_id: {"score": None}
    
    print(f"\n[Test Case] Start: {current_price}, Target: {target_price}, Step: 0.40")
    
    result = engine.calculate_safe_price_steps("test_item", current_price, target_price)
    steps = result['steps']
    total_steps = len(steps)
    
    print(f"Total Steps Generated: {total_steps}")
    
    expected_steps = 5
    if total_steps == expected_steps:
        print("PASS: Correct number of steps (5).")
    else:
        print(f"FAIL: Expected {expected_steps}, got {total_steps}.")
        
    # Check Step Values
    all_correct = True
    for i, step in enumerate(steps):
        expected_price = 100.00 + ((i + 1) * 0.40)
        # Round logic in engine is round(p, 2)
        if abs(step['price'] - expected_price) > 0.01:
            print(f"FAIL Step {i+1}: Expected {expected_price}, Got {step['price']}")
            all_correct = False
    
    if all_correct:
         print("PASS: All step prices correct.")
         
    # Check Dates (1 day apart)
    date_1 = datetime.strptime(steps[0]['date'], "%Y-%m-%d")
    date_2 = datetime.strptime(steps[1]['date'], "%Y-%m-%d")
    delta = (date_2 - date_1).days
    if delta == 1:
        print(f"PASS: Date interval is {delta} day.")
    else:
        print(f"FAIL: Date interval is {delta} days (Expected 1).")

if __name__ == "__main__":
    test_fixed_pricing_logic()
