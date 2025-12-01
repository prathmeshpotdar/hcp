from sqlalchemy.orm import Session
from .models import Interaction
from datetime import datetime

def create_interaction(db: Session, data: dict, raw_text: str):
    obj = Interaction(
        raw_text = raw_text,
        hcp_name = data.get("hcp_name"),
        date = data.get("date"),
        time = data.get("time"),
        topics_discussed = data.get("topics_discussed"),
        materials_shared = data.get("materials_shared") or [],
        samples_distributed = data.get("samples_distributed") or [],
        sentiment = data.get("sentiment"),
        sentiment_source = data.get("sentiment_source"),
        outcomes = data.get("outcomes"),
        follow_up_date = data.get("follow_up_date"),
        summary = data.get("summary"),
        created_at = datetime.utcnow()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_interaction(db: Session, interaction_id: str):
    return db.query(Interaction).filter(Interaction.id == interaction_id).first()

def update_interaction(db: Session, interaction_id: str, updates: dict):
    obj = get_interaction(db, interaction_id)
    if not obj:
        return None
    for k, v in updates.items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj
