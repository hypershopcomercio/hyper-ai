from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, unique=True, index=True, default="mercadolivre")
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    seller_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
