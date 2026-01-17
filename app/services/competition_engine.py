
import logging
from sqlalchemy.orm import Session
from app.models.competitor_ad import CompetitorAd
from app.services.meli_api import MeliApiService
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class CompetitionEngine:
    def __init__(self, db: Session):
        self.db = db
        self.meli_service = MeliApiService(db_session=db)

    def extract_id_from_url(self, url: str) -> str:
        # Tries to find MLB...ID
        match = re.search(r'(MLB\d{9,})', url) # Usually MLB + digits
        if not match:
            # Try with hyphen
            match = re.search(r'(MLB-\d{9,})', url)
        
        if match:
             return match.group(1).replace('-', '')
        return None

    def add_competitor(self, my_ad_id: str, competitor_url: str):
        comp_id = self.extract_id_from_url(competitor_url)
        if not comp_id:
            # If user pasted just ID
            if competitor_url.upper().startswith("MLB"):
                 comp_id = competitor_url.upper().replace('-', '')
            else:
                 raise ValueError("Could not extract MLB ID from Link")

        # Check if already exists
        exists = self.db.query(CompetitorAd).filter(
            CompetitorAd.ad_id == my_ad_id,
            CompetitorAd.competitor_id == comp_id
        ).first()
        
        if exists:
            return exists

        # Fetch Initial Data (Public)
        # We use a probing method or MeliService specific for public items
        # assuming get_item_details works for single item or we need a public fetcher
        # Since probing failed 403, we might have issues if we don't have a token or correct headers.
        # But let's assume MeliApiService has a method or we add one.
        # actually, MeliApiService uses a specific token method.
        # Let's try to fetch via MeliApiService.get_item_details([id])
        
        try:
            details_list = self.meli_service.get_item_details([comp_id])
            if not details_list:
                raise ValueError("Competitor ID not found in API")
            
            item = details_list[0]
            
            comp = CompetitorAd(
                competitor_id=comp_id,
                ad_id=my_ad_id,
                title=item.get('title'),
                price=float(item.get('price', 0)),
                original_price=float(item.get('original_price')) if item.get('original_price') else None,
                permalink=item.get('permalink'),
                seller_name="Competitor", # Often verifying seller requires extra call
                status=item.get('status'),
                last_updated=datetime.now()
            )
            self.db.add(comp)
            self.db.commit()
            return comp
            
        except Exception as e:
            logger.error(f"Failed to fetch initial data for {comp_id}: {e}")
            # Fallback: Create with Pending status
            comp = CompetitorAd(
                competitor_id=comp_id,
                ad_id=my_ad_id,
                title=f"Aguardando Sincronização ({comp_id})",
                price=0.0,
                permalink=competitor_url,
                seller_name="Competitor",
                status="pending",
                last_updated=datetime.now()
            )
            self.db.add(comp)
            self.db.commit()
            return comp

    def get_competitors(self, ad_id: str):
        return self.db.query(CompetitorAd).filter(CompetitorAd.ad_id == ad_id).all()

    def update_competitor_prices(self, ad_id: str):
        """
        Updates prices for all competitors of a specific ad using the ML API.
        """
        competitors = self.get_competitors(ad_id)
        if not competitors:
            return 0
            
        updated_count = 0
        
        # Get all competitor IDs
        comp_ids = [comp.competitor_id for comp in competitors if comp.competitor_id]
        
        if not comp_ids:
            return 0
            
        try:
            # Fetch all items in one API call (batched)
            details_list = self.meli_service.get_item_details(comp_ids)
            
            if not details_list:
                logger.warning(f"No data returned from API for competitors of {ad_id}")
                return 0
                
            # Create a lookup map
            details_map = {item.get('id'): item for item in details_list if item}
            
            for comp in competitors:
                item = details_map.get(comp.competitor_id)
                if item:
                    new_price = float(item.get('price', 0))
                    new_original = float(item.get('original_price')) if item.get('original_price') else None
                    new_status = item.get('status', 'active')
                    new_title = item.get('title', comp.title)
                    
                    # Update fields
                    if new_price > 0:
                        comp.price = new_price
                    if new_original:
                        comp.original_price = new_original
                    comp.status = new_status
                    comp.title = new_title
                    comp.last_updated = datetime.now()
                    updated_count += 1
                else:
                    logger.warning(f"No API data for competitor {comp.competitor_id}")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating competitors via API: {e}")
            
        return updated_count
