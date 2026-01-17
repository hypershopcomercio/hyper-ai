from app.core.database import SessionLocal
from app.services.forecast import HyperForecast
from app.models.product_forecast import ProductForecast
from datetime import datetime

db = SessionLocal()
try:
    print("--- INSPECTING FORECAST VALUES ---")
    
    # 1. Check Global Multipliers
    forecast = HyperForecast(db)
    now = datetime.now()
    hour = now.hour
    
    print(f"\nTime: {now}, Hour: {hour}")
    
    prediction = forecast.predict_hour(hour, now.date())
    print("\nGlobal Multiplier Breakdown:")
    print(f"Combined Multiplier: {prediction['combined_multiplier']}")
    for k, v in prediction['multipliers'].items():
        print(f"  {k}: {v}")

    # 2. Check Product Base Units
    print("\n--- PRODUCT BASE UNITS (Top 5) ---")
    products = db.query(ProductForecast).limit(5).all()
    
    for p in products:
        print(f"ID: {p.mlb_id}")
        print(f"  Title: {p.title[:30]}...")
        print(f"  Avg Units (7d): {p.avg_units_7d}")
        print(f"  Price: {p.price}")
        if p.avg_units_7d:
             daily_rev = float(p.avg_units_7d) * float(p.price)
             print(f"  Implied Daily Rev (Base): R${daily_rev:.2f}")

finally:
    db.close()
