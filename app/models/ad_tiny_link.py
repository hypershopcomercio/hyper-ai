from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class AdTinyLink(Base):
    __tablename__ = "ad_tiny_links"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String, ForeignKey("ads.id"), nullable=False, index=True)
    tiny_product_id = Column(String, ForeignKey("tiny_products.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
