"""
Promotion Service - Manages ML Deals API for promotions.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.meli_api import MeliApiService

logger = logging.getLogger(__name__)


class PromoService:
    """Service for managing Mercado Livre promotions via API."""
    
    def __init__(self, db: Session):
        self.db = db
        self.meli = MeliApiService(db)
    
    def get_item_promotions(self, item_id: str) -> dict:
        """
        Get all active promotions for an item.
        
        Endpoint: GET /seller-promotions/items/{item_id}
        
        Returns:
            {
                "has_promotions": bool,
                "promotions": [
                    {
                        "type": "PRICE_DISCOUNT",
                        "deal_price": 119.45,
                        "original_price": 149.90,
                        "discount_percent": 20.3,
                        "start_date": "2026-01-11",
                        "finish_date": "2026-01-25",
                        "status": "active"
                    }
                ],
                "error": str | None
            }
        """
        try:
            response = self.meli.request("GET", f"/seller-promotions/items/{item_id}")
            
            if not response:
                return {"has_promotions": False, "promotions": [], "error": "No response"}
            
            promotions = []
            
            # Parse response - format varies by promotion type
            if isinstance(response, list):
                for promo in response:
                    promotions.append(self._parse_promotion(promo))
            elif isinstance(response, dict):
                # Single promotion or error
                if "error" in response:
                    return {"has_promotions": False, "promotions": [], "error": response.get("message")}
                promotions.append(self._parse_promotion(response))
            
            return {
                "has_promotions": len(promotions) > 0,
                "promotions": promotions,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error getting promotions for {item_id}: {e}")
            return {"has_promotions": False, "promotions": [], "error": str(e)}
    
    def _parse_promotion(self, promo: dict) -> dict:
        """Parse promotion data from ML API response."""
        deal_price = promo.get("deal_price") or promo.get("price")
        original_price = promo.get("original_price") or promo.get("list_price")
        
        discount_percent = 0
        if original_price and deal_price and original_price > 0:
            discount_percent = ((original_price - deal_price) / original_price) * 100
        
        return {
            "type": promo.get("type") or promo.get("promotion_type"),
            "deal_price": deal_price,
            "original_price": original_price,
            "discount_percent": round(discount_percent, 1),
            "start_date": promo.get("start_date"),
            "finish_date": promo.get("finish_date"),
            "status": promo.get("status", "active")
        }
    
    def get_available_deals(self, item_id: str) -> dict:
        """
        Get available deal types that can be applied to an item.
        
        Returns:
            {
                "deals": [
                    {"type": "PRICE_DISCOUNT", "name": "Desconto por Porcentagem", "max_discount": 70},
                ]
            }
        """
        # For now, return standard deal types available
        # In future, query ML API for item-specific eligibility
        return {
            "deals": [
                {
                    "type": "PRICE_DISCOUNT",
                    "name": "Desconto por Porcentagem",
                    "description": "Aplica desconto de até 70% por até 14 dias",
                    "max_discount": 70,
                    "max_days": 14
                },
            ],
            "error": None
        }
    
    def apply_promotion(self, item_id: str, deal_price: float, days: int = 14) -> dict:
        """
        Apply a PRICE_DISCOUNT promotion to an item.
        
        Args:
            item_id: MLB item ID
            deal_price: The discounted price
            days: Duration in days (max 14)
        
        Returns:
            {"success": bool, "error": str | None}
        """
        try:
            start_date = datetime.now().strftime("%Y-%m-%d")
            finish_date = (datetime.now() + timedelta(days=min(days, 14))).strftime("%Y-%m-%d")
            
            payload = {
                "promotion_type": "PRICE_DISCOUNT",
                "deal_price": deal_price,
                "start_date": start_date,
                "finish_date": finish_date
            }
            
            response = self.meli.request(
                "POST", 
                f"/seller-promotions/items/{item_id}",
                json_data=payload
            )
            
            if response and not response.get("error"):
                logger.info(f"Applied promotion to {item_id}: R${deal_price}")
                return {"success": True, "error": None, "promotion": response}
            
            error_msg = response.get("message") if response else "Unknown error"
            logger.error(f"Failed to apply promotion to {item_id}: {error_msg}")
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"Error applying promotion to {item_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def remove_promotion(self, item_id: str, promo_type: str = "PRICE_DISCOUNT") -> dict:
        """
        Remove a promotion from an item.
        
        Endpoint: DELETE /seller-promotions/items/{item_id}/type/{promotion_type}
        """
        try:
            response = self.meli.request(
                "DELETE",
                f"/seller-promotions/items/{item_id}/type/{promo_type}"
            )
            
            # DELETE usually returns 200/204 on success
            return {"success": True, "error": None}
            
        except Exception as e:
            logger.error(f"Error removing promotion from {item_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_promotion_params(
        self, 
        current_effective_price: float,
        desired_margin_percent: float,
        total_costs: float
    ) -> dict:
        """
        Calculate the original price and deal price needed for a desired margin.
        
        Strategy: Set original price higher to allow promotional discount.
        
        Args:
            current_effective_price: Current selling price
            desired_margin_percent: Target margin (e.g., 15 for 15%)
            total_costs: All costs (product + fees + shipping)
        
        Returns:
            {
                "original_price": float,  # Price to set as base
                "deal_price": float,      # Promotional price
                "discount_percent": float # Resulting discount
            }
        """
        # Calculate deal price from desired margin
        # Margin = (Price - Costs) / Price * 100
        # Price = Costs / (1 - Margin/100)
        margin_dec = desired_margin_percent / 100
        
        if margin_dec >= 1:
            margin_dec = 0.5  # Cap at 50%
        
        deal_price = total_costs / (1 - margin_dec)
        
        # Original price should be higher to show discount
        # Typically 20-30% above deal price for good visual impact
        original_price = deal_price * 1.25  # 25% markup
        
        discount_percent = ((original_price - deal_price) / original_price) * 100
        
        return {
            "original_price": round(original_price, 2),
            "deal_price": round(deal_price, 2),
            "discount_percent": round(discount_percent, 1)
        }
