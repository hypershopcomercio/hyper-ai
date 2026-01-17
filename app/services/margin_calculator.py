
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
        
    def calculate_margin(self, ad: Ad, tiny_product: TinyProduct = None, tax_rate: float = 0.0, fixed_cost: float = 0.0, inbound_cost: float = 0.0):
        """
        Calculates margin: Net Revenue - (Product Cost + Purchase Taxes + Sales Taxes + Fixed Costs + Inbound Costs).
        Uses effective_price (promotion_price if lower than price) for accurate margin calculation.
        """
        if not ad.price:
            return
        
        # Use standard price (Revert Promotion Logic)
        effective_price = ad.price
            
        # 1. Commission (based on effective price)
        commission_rate = 0.16 if ad.listing_type_id == "gold_pro" else 0.11
        commission_cost = effective_price * commission_rate
        
        # 2. Shipping
        shipping_cost = ad.shipping_cost if ad.shipping_cost else 0.0
        
        # 3. Net Revenue
        net_revenue = effective_price - commission_cost - shipping_cost
        
        # 4. Total Product Cost (Base + Taxes)
        base_cost = tiny_product.cost if tiny_product and tiny_product.cost else (ad.cost if ad.cost else 0.0)
        purchase_tax = self._calculate_purchase_tax(tiny_product) if tiny_product else 0.0
        
        total_product_cost = base_cost + purchase_tax
        
        # 5. Sales Tax (DAS) - based on effective price
        sales_tax_cost = effective_price * (tax_rate / 100.0)

        # 6. Fixed Costs (Packaging, etc) & Inbound Costs (Full)
        # fixed_cost is passed as absolute value per sale
        
        # 7. Total Deductions
        # Margin Formula: Sale Price - (Commission + Shipping + Taxes + Product + Fixed + Inbound)
        
        gross_profit = effective_price - commission_cost - shipping_cost - total_product_cost - sales_tax_cost - fixed_cost - inbound_cost
        
        # 8. Margin %
        margin_percent = (gross_profit / effective_price) * 100 if effective_price > 0 else 0.0
        
        # 9. Suggested Price (Reverse Calculation)
        # Target: Net Margin % (Default 15% if not set)
        target = ad.target_margin if ad.target_margin is not None else 0.15
        
        # Formula: Price = (Product + Shipping + Fixed + Inbound) / (1 - (TaxRate + CommissionRate + Target))
        # Denominator check
        variable_rates = (tax_rate / 100.0) + commission_rate + target
        
        if variable_rates < 1.0:
            total_fixed_costs = total_product_cost + shipping_cost + fixed_cost + inbound_cost
            suggested = total_fixed_costs / (1.0 - variable_rates)
            # ONLY update suggested_price if there's NO active strategy
            # An active strategy has strategy_start_price set - we don't want to overwrite it
            if not ad.strategy_start_price or ad.strategy_start_price == 0:
                ad.suggested_price = suggested
        else:
            # Only set to 0 if no active strategy
            if not ad.strategy_start_price or ad.strategy_start_price == 0:
                ad.suggested_price = 0.0 # Impossible target (costs > 100%)

        # Update Ad
        ad.commission_cost = commission_cost
        ad.tax_cost = purchase_tax + sales_tax_cost # Total Taxes (Purchase+Sales)
        ad.margin_value = gross_profit
        ad.margin_percent = margin_percent
        ad.is_margin_alert = margin_percent < 20.0
        
        return ad
