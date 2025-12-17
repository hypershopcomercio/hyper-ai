
from sqlalchemy import Column, String, Text
from app.core.database import Base

class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text) # Storing as string, cast as needed
    description = Column(String(255), nullable=True)
    group = Column(String(50), nullable=True) # 'tax', 'sync', 'general'
