from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.db import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    owner_email = Column(String)  # Pemilik dataset

    created_at = Column(DateTime, default=datetime.utcnow)