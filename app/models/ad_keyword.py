
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from app.models.base import Base

class AdKeyword(Base):
    __tablename__ = "ad_keywords"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String, ForeignKey("ads.id"), nullable=False)
    
    keyword = Column(String, nullable=False)
    position = Column(Integer, nullable=True) # e.g. 1, 5, 20
    page = Column(Integer, nullable=True) # e.g. 1, 2
    
    search_volume_label = Column(String, nullable=True) # e.g. "Dominante", "Nicho"
    last_updated = Column(DateTime, default=datetime.now)
