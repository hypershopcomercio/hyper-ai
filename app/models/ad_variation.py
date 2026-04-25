
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AdVariation(Base):
    __tablename__ = "ad_variations"

    id = Column(String(255), primary_key=True, index=True) # ML Variation ID
    ad_id = Column(String(255), ForeignKey("ads.id"), index=True)
    sku = Column(String(255), index=True, nullable=True)
    
    # Financials
    price = Column(Float)
    available_quantity = Column(Integer)
    cost = Column(Float, default=0.0) # From Tiny
    tax_cost = Column(Float, default=0.0) # Calculated
    
    # Details
    attribute_combination = Column(String(500), nullable=True) # e.g. "Cor: Vermelho, Tamanho: G"
    picture_ids = Column(JSON)
    seller_custom_field = Column(String(255))
    
    # Relationships
    # ad = relationship("Ad", back_populates="variations")

