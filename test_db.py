import os
from dotenv import load_dotenv
load_dotenv('C:/Users/Michel/Documents/hyper-ai/.env')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print('--- DESCRIBE ad_variations ---')
    res = db.execute(text('DESCRIBE ad_variations'))
    for row in res:
        print(row)
        
    print('\n--- SEARCH Forno Variations ---')
    res2 = db.execute(text("SELECT id, ad_id, sku, attribute_combination, seller_custom_field FROM ad_variations WHERE attribute_combination LIKE '%220V%' OR attribute_combination LIKE '%127V%' LIMIT 5"))
    for row in res2:
        print(row)
        
    print('\n--- SEARCH Forno Ads ---')
    res3 = db.execute(text("SELECT id, sku, title, gtin, catalog_product_id FROM ads WHERE title LIKE '%Forno%' LIMIT 5"))
    for row in res3:
        print(row)
except Exception as e:
    print("Error:", e)
finally:
    db.close()
