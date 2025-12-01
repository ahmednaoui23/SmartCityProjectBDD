from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class CapteurBase(BaseModel):
    type_capteur: str
    latitude: Optional[float]
    longitude: Optional[float]
    statut: Optional[str]
    date_installation: Optional[datetime]
    id_proprietaire: Optional[int]
    id_arrondissement: Optional[int]

class CapteurCreate(CapteurBase):
    pass

class CapteurOut(CapteurBase):
    uuid_capteur: UUID
    class Config:
        model_config = {
            "from_attributes": True
        }