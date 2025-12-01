from pydantic import BaseModel
from typing import List, Optional

class ChatIn(BaseModel):
    text: str

class InteractionOut(BaseModel):
    interaction_id: str
    hcp_name: Optional[str]
    date: Optional[str]
    time: Optional[str]
    topics_discussed: Optional[str]
    materials_shared: List[str] = []
    samples_distributed: List[str] = []
    sentiment: Optional[str]
    sentiment_source: Optional[str]
    outcomes: Optional[str]
    follow_up_date: Optional[str]
    summary: Optional[str]
    created_at: Optional[str]
    message: str
