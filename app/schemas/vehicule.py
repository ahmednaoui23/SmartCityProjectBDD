from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class VehiculeCreate(BaseModel):
    plaque: str
    type_vehicule: Optional[str]
    energie: Optional[str]

class VehiculeOut(VehiculeCreate):
    class Config:
        orm_mode = True

class TrajetCreate(BaseModel):
    origine: Optional[str]
    destination: Optional[str]
    distance_km: Optional[Decimal]
    duree_minutes: Optional[int]
    co2_economie: Optional[Decimal]
    date_heure: Optional[datetime]
    plaque: Optional[str]

class TrajetOut(TrajetCreate):
    class Config:
        model_config = {
            "from_attributes": True
        }