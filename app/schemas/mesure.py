from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class MesureCreate(BaseModel):
    uuid_capteur: UUID
    ts: datetime
    pollutant: str
    valeur: Decimal
    unite: Optional[str]

class MesureOut(MesureCreate):
    id: int
    class Config:
        model_config = {
            "from_attributes": True
        }