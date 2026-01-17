import sys
import os

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
    def __init__(self, ad_data):
        self.ad_data = ad_data
    def query(self, *args):
        return MockQuery([self.ad_data])

def test_breakeven_logic():
    print(">>> Testing Break-even Logic...")
    
    # Setup Ad Data
    # P = 100, Cost = 40, Ship = 10, TaxCost = 10 (10%), CommPct = 0.
    # Margin Value = 100 - 10 - 10 - 40 = 40.
    # Conv = 5% (Total Visits 100, Sold 5)
    
    ad = Ad(
        id="test_item",
        price=100.0,
        cost=40.0,
        shipping_cost=10.0,
        tax_cost=10.0,
        commission_percent=0.0,
        margin_value=40.0,
        sold_quantity=5,
        total_visits=100
    )
    
    db = MockDB(ad)
    engine = PricingEngine(db)
    
    # Test 1: Price Increase to 120
    # New Tax = 120 * 0.10 = 12.
    # New Margin = 120 - 12 - 10 - 40 = 58.
    # Old Profit Per Visitor = 40 * 0.05 = 2.0.
    # New Conv Needed = 2.0 / 58 = 0.03448... -> 3.45%
    
    print("\n[Scenario 1] Price Increase 100 -> 120")
    be_conv = engine.calculate_break_even_conversion("test_item", 120.0)
    print(f"Break-even Conv: {be_conv}%")
    
    expected = 3.45
    if abs(be_conv - expected) < 0.1:
        print("PASS: Correctly calculated lower conversion requirement.")
    else:
        print(f"FAIL: Expected ~{expected}%, got {be_conv}%")

    # Test 2: Price Decrease to 90
    # New Tax = 9 (10%)
    # New Margin = 90 - 9 - 10 - 40 = 31.
    # Old Profit Per Visitor = 2.0.
    # New Conv Needed = 2.0 / 31 = 0.0645... -> 6.45%
    
    print("\n[Scenario 2] Price Decrease 100 -> 90")
    be_conv_low = engine.calculate_break_even_conversion("test_item", 90.0)
    print(f"Break-even Conv: {be_conv_low}%")
    
    expected_low = 6.45
    if abs(be_conv_low - expected_low) < 0.1:
        print("PASS: Correctly calculated higher conversion requirement.")
    else:
        print(f"FAIL: Expected ~{expected_low}%, got {be_conv_low}%")

if __name__ == "__main__":
    test_breakeven_logic()
