
import logging
from app.models.ad import Ad
from app.models.tiny_product import TinyProduct

logger = logging.getLogger(__name__)

class MarginCalculatorService:
    def __init__(self):
        # Configuration could be moved to settings or DB
        self.tax_rate = 0.0 # Placeholder
        self.fixed_cost = 0.0 # Any per-sale fixed cost?
        
    def _calculate_purchase_tax(self, tiny_product: TinyProduct) -> float:
        """
        Calculates Additional Purchase Taxes (DIFAL) to form the Total Product Cost.
        """
        if not tiny_product or not tiny_product.cost:
            return 0.0

        # Current logic: Disable automatic DIFAL and trust imported Cost.
        return 0.0
        
    def calculate_margin(self, ad: Ad, tiny_product: TinyProduct = None, tax_rate: float = 0.0, fixed_cost: float = 0.0):
        """
        Calculates margin: Net Revenue - (Product Cost + Purchase Taxes + Sales Taxes + Fixed Costs).
        """
        if not ad.price:
            return
            
        # 1. Commission
        commission_rate = 0.16 if ad.listing_type_id == "gold_pro" else 0.11
        commission_cost = ad.price * commission_rate
        
        # 2. Shipping
        shipping_cost = ad.shipping_cost if ad.shipping_cost else 0.0
        
        # 3. Net Revenue
        net_revenue = ad.price - commission_cost - shipping_cost
        
        # 4. Total Product Cost (Base + Taxes)
        base_cost = tiny_product.cost if tiny_product and tiny_product.cost else (ad.cost if ad.cost else 0.0)
        purchase_tax = self._calculate_purchase_tax(tiny_product) if tiny_product else 0.0
        
        total_product_cost = base_cost + purchase_tax
        
        # 5. Sales Tax (DAS)
        sales_tax_cost = ad.price * (tax_rate / 100.0)

        # 6. Fixed Costs (Packaging, etc)
        # fixed_cost is passed as absolute value per sale
        
        # 7. Total Deductions
        # Note: Shipping is already deducted from Net Revenue, or should be part of cost? 
        # Margin Formula usually: Sale Price - (Commission + Shipping + Taxes + Product + Fixed)
        # Gross Profit (Margem de Contribuição)
        
        gross_profit = ad.price - commission_cost - shipping_cost - total_product_cost - sales_tax_cost - fixed_cost
        
        # 8. Margin %
        margin_percent = (gross_profit / ad.price) * 100 if ad.price > 0 else 0.0
        
        # Update Ad
        ad.commission_cost = commission_cost
        ad.tax_cost = purchase_tax + sales_tax_cost # Total Taxes (Purchase+Sales)
        ad.margin_value = gross_profit
        ad.margin_percent = margin_percent
        ad.is_margin_alert = margin_percent < 20.0
        
        return ad
