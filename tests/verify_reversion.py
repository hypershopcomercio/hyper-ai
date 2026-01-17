import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.pricing_engine import PricingEngine
from app.models.ml_metrics_daily import MlMetricsDaily
from app.models.ad import Ad

# Mock classes to avoid full DB setup
class MockQuery:
    def __init__(self, data):
        self.data = data
        
    def filter(self, *args, **kwargs):
        # Very simple mock filter - returns self to allow chaining or a filtered list
        return self

    def first(self):
        return self.data[0] if self.data else None
        
    def all(self):
        return self.data
    
    def label(self, name):
        return self # simplified

class MockDB:
    def query(self, *args):
        # We need to determine what is being queried to return appropriate MockQuery
        # This is a bit tricky with args which are columns.
        # Check first arg.
        first_arg = args[0]
        
        # If querying for sum (tuple likely), we return a Mock object that acts like a result row
        if str(first_arg).startswith("sum("):
             # This is the 7d metrics query
             # Let's assume we are testing the "Drop" scenario first
             # Scenario: 7d avg is 5%, Today is 2%
             return MockQuery([MockMetricsSum(total_sales=35, total_visits=700)]) # 35/700 = 5%
        
        # If querying MlMetricsDaily entity (Today's metric)
        if first_arg == MlMetricsDaily:
            return MockQuery([MlMetricsDaily(sales_qty=2, visits=100)]) # 2/100 = 2%

        # If querying Ad
        if first_arg == Ad:
            return MockQuery([Ad(id="test_item", total_visits=1000, sold_quantity=50)])

        return MockQuery([])

class MockMetricsSum:
    def __init__(self, total_sales, total_visits):
        self.total_sales = total_sales
        self.total_visits = total_visits

def test_reversion_logic():
    print(">>> Testing Automatic Reversion Logic...")
    
    # Setup
    db = MockDB()
    engine = PricingEngine(db)
    
    # 1. Test Drop Scenario
    # 7d Avg: 35 sales / 700 visits = 5%
    # Today: 2 sales / 100 visits = 2%
    # Drop: (5 - 2) / 5 = 60% drop -> SHOULD TRIGGER
    
    print("\n[Scenario 1] High Drop (60%)")
    result = engine.check_auto_reversion_status("test_item")
    print(f"Result: {result}")
    
    if result['triggered'] and result['drop_pct'] == 60.0:
        print("PASS: Detected drop correctly.")
    else:
        print("FAIL: Did not detect drop correctly.")

    # 2. Test Stable Scenario
    # We need to monkeypatch the DB for this or make the MockDB smarter.
    # Let's monkeypatch the db.query instance method for a second test
    
    print("\n[Scenario 2] Stable (No Drop)")
    # 7d Avg: 5% (Same)
    # Today: 5 sales / 100 visits = 5%
    
    original_query = db.query
    
    def mock_query_stable(*args):
        first_arg = args[0]
        if str(first_arg).startswith("sum("):
             return MockQuery([MockMetricsSum(total_sales=35, total_visits=700)]) # 5%
        if first_arg == MlMetricsDaily:
            return MockQuery([MlMetricsDaily(sales_qty=5, visits=100)]) # 5%
        return MockQuery([])
        
    db.query = mock_query_stable
    
    result_stable = engine.check_auto_reversion_status("test_item")
    print(f"Result: {result_stable}")
    
    if not result_stable['triggered'] and result_stable['drop_pct'] == 0.0:
        print("PASS: Correctly ignored stable conversion.")
    else:
        print("FAIL: False positive on stable conversion.")

if __name__ == "__main__":
    test_reversion_logic()
