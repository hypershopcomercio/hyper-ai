
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from app.core.database import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    module = Column(String(50), index=True) # e.g., 'sync_engine', 'meli_auth'
    level = Column(String(20)) # 'INFO', 'ERROR', 'WARNING'
    message = Column(Text)
    details = Column(Text, nullable=True) # JSON or stacktrace
    duration_ms = Column(Integer, nullable=True)
