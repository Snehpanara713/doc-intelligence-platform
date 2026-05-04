from sqlalchemy import Column, String, JSON
from app.db.database import Base

class EnvelopeAudit(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    envelope_id = Column(String)
    data = Column(JSON)