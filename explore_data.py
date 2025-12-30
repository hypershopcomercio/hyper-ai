"""Explore existing database data for product forecast implementation"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.tiny_product import TinyProduct
from app.models.tiny_stock import TinyStock
from sqlalchemy import func, text
from datetime import datetime, timedelta

def explore_data():
    db = SessionLocal()
    
    print("=" * 60)
    print("EXPLORAÇÃO DE DADOS PARA FORECAST POR PRODUTO")
    print("=" * 60)
    
    # 1. Count products
    ad_count = db.query(Ad).count()
    print(f"\n1. PRODUTOS (Ads): {ad_count} anúncios")
    
    # Sample products with stock info
    sample_ads = db.query(Ad).filter(Ad.status == 'active').limit(5).all()
    print("\n   Amostra de produtos ativos:")
    for ad in sample_ads:
        print(f"   - {ad.id}: {ad.title[:50]}...")
        print(f"     Categoria: {ad.category_name}")
        print(f"     Estoque ML: {ad.available_quantity} | Estoque Tiny: {ad.stock_tiny}")
        print(f"     Vendas 30d: {ad.sales_30d} | Preço: R${ad.price}")
        print()
    
    # 2. Check categories
    categories = db.query(Ad.category_name, func.count(Ad.id)).group_by(Ad.category_name).all()
    print(f"\n2. CATEGORIAS: {len(categories)} categorias únicas")
    for cat, count in categories[:10]:
        print(f"   - {cat}: {count} produtos")
    
    # 3. Check sales data
    order_count = db.query(MlOrder).count()
    item_count = db.query(MlOrderItem).count()
    print(f"\n3. VENDAS: {order_count} pedidos, {item_count} itens")
    
    # Sales last 7 days by product
    week_ago = datetime.now() - timedelta(days=7)
    sales_by_product = db.query(
        MlOrderItem.ml_item_id,
        func.sum(MlOrderItem.quantity).label('qty'),
        func.sum(MlOrderItem.unit_price * MlOrderItem.quantity).label('revenue')
    ).join(MlOrder).filter(
        MlOrder.date_closed >= week_ago,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(MlOrderItem.ml_item_id).order_by(func.sum(MlOrderItem.quantity).desc()).limit(10).all()
    
    print("\n   Top 10 produtos por quantidade vendida (últimos 7d):")
    for mlb_id, qty, revenue in sales_by_product:
        ad = db.query(Ad).filter(Ad.id == mlb_id).first()
        title = ad.title[:40] if ad else "?"
        stock = ad.available_quantity if ad else "?"
        print(f"   - {mlb_id}: {qty} un | R${float(revenue):.2f} | Estoque: {stock}")
        print(f"     {title}...")
    
    # 4. Check Tiny stock
    tiny_stock_count = db.query(TinyStock).count()
    print(f"\n4. TINY STOCK: {tiny_stock_count} registros")
    
    # 5. Check products with zero stock
    zero_stock = db.query(Ad).filter(Ad.available_quantity == 0, Ad.status == 'active').count()
    print(f"\n5. PRODUTOS SEM ESTOQUE (ativos): {zero_stock}")
    
    db.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    explore_data()
