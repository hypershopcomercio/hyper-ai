
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MlVisit(Base):
    __tablename__ = "ml_visits"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    visits = Column(Integer, default=0)
    source = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
