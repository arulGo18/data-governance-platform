from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String)
    action = Column(String)
    endpoint = Column(String)
    method = Column(String)

    status_code = Column(Integer)        
    latency_ms = Column(Integer)        
    ip_address = Column(String)        

    timestamp = Column(DateTime, default=datetime.utcnow)