from sqlalchemy import Column, String, DateTime, Text, JSON
from datetime import datetime
from .database import Base
import uuid

def make_uuid():
    return str(uuid.uuid4())

class Interaction(Base):
    __tablename__ = "interaction"

    id = Column(String, primary_key=True, default=make_uuid)
    raw_text = Column(Text, nullable=True)

    hcp_name = Column(String, nullable=True)
    date = Column(String, nullable=True)           # ISO YYYY-MM-DD
    time = Column(String, nullable=True)           # HH:MM (24h)

    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(JSON, nullable=True)
    samples_distributed = Column(JSON, nullable=True)

    sentiment = Column(String, nullable=True)         # Positive/Neutral/Negative
    sentiment_source = Column(String, nullable=True)  # observed / inferred / None

    outcomes = Column(Text, nullable=True)
    follow_up_date = Column(String, nullable=True)    # ISO

    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
