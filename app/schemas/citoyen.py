from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class CitoyenCreate(BaseModel):
    nom: Optional[str]
    adresse: Optional[str]
    email: Optional[str]
    score_engagement: Optional[Decimal]
    preferences_mobilite: Optional[dict]

class CitoyenOut(CitoyenCreate):
    id_citoyen: int
    class Config:
        model_config = {
            "from_attributes": True
        }