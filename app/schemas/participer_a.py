from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ParticiperACreate(BaseModel):
    id_citoyen: int
    id_consultation: int
    avis: Optional[str]
    vote: Optional[int]
    date_participation: Optional[datetime]

class ParticiperAOut(ParticiperACreate):
    class Config:
        model_config = {
            "from_attributes": True
        }