
from itertools import combinations

orders = [
    {"id": "2000014419924860", "val": 133.99},
    {"id": "2000014275865562", "val": 9.90},
    {"id": "2000014149744094", "val": 149.90},
    {"id": "2000014125868728", "val": 169.90},
    {"id": "2000014099782270", "val": 119.90},
    {"id": "2000014184013300", "val": 129.90},
    {"id": "2000014174080278", "val": 159.90},
    {"id": "2000014200611830", "val": 87.20},
    {"id": "2000014192882622", "val": 86.53},
    {"id": "2000014264362110", "val": 164.90},
    {"id": "2000014253713928", "val": 113.98},
    {"id": "2000014220300020", "val": 87.20},
    {"id": "2000014285203234", "val": 149.90},
    {"id": "2000014293954164", "val": 179.90},
    {"id": "2000014415555248", "val": 189.90},
    {"id": "2000014425495124", "val": 114.61},
    {"id": "2000014251471180", "val": 114.61},
    {"id": "2000014369197480", "val": 133.99},
    {"id": "2000014082729494", "val": 99.90},
    {"id": "2000014330625710", "val": 168.20},
    {"id": "2000014381569110", "val": 164.90},
    {"id": "2000014403184862", "val": 219.90},
    {"id": "2000014398248646", "val": 179.90},
    {"id": "2000014410686664", "val": 164.90}
]

target = 463.06 # (97270.06 - 96807 = 463.06)
diff = 463.06 

print(f"Target Sum: {diff}")

# Find subset summing to roughly 851.81 (+/- 2.0)
from itertools import combinations

def solve():
    vals = [o['val'] for o in orders]
    n = len(vals)
    
    # Try combinations of 3, 4, 5, 2, 6...
    # ML Count diff is 3 orders?
    # Or 4?
    # Let's try 3 first.
    
    found = False
    
    for r in range(1, 7):
        print(f"Checking size {r}...")
        for c in combinations(orders, r):
            s = sum(o['val'] for o in c)
            if abs(s - diff) < 2.0:
                print(f"FOUND MATCH! Sum: {s}")
                for x in c:
                    print(x)
                found = True
                return
                
    if not found:
        print("No match found.")

if __name__ == "__main__":
    solve()
