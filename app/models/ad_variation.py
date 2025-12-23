
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AdVariation(Base):
    __tablename__ = "ad_variations"

    id = Column(String, primary_key=True, index=True) # ML Variation ID
    ad_id = Column(String, ForeignKey("ads.id"), index=True)
    sku = Column(String, index=True, nullable=True)
    
    # Financials
    price = Column(Float)
    available_quantity = Column(Integer)
    cost = Column(Float, default=0.0) # From Tiny
    tax_cost = Column(Float, default=0.0) # Calculated
    
    # Details
    attribute_combination = Column(String, nullable=True) # e.g. "Cor: Vermelho, Tamanho: G"
    picture_ids = Column(JSON)
    seller_custom_field = Column(String)
    
    # Relationships
    # ad = relationship("Ad", back_populates="variations")

