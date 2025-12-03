from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class InterventionCreate(BaseModel):
    date_heure: datetime
    nature: Optional[str]
    duree_minutes: Optional[int]
    cout: Optional[Decimal]
    impact_co2: Optional[Decimal]
    ia_valide: Optional[bool] = False
    uuid_capteur: Optional[UUID]

class InterventionOut(InterventionCreate):
    class Config:
        model_config = {
            "from_attributes": True
        }