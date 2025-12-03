from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CapteurBase(BaseModel):
    type_capteur: str
    latitude: Optional[float]
    longitude: Optional[float]
    statut: Optional[str]
    date_installation: Optional[datetime]
    # On retire les id internes de la sortie
    # id_proprietaire: Optional[int]
    # id_arrondissement: Optional[int]

class CapteurCreate(CapteurBase):
    # On garde tout pour la création
    pass

class CapteurOut(CapteurBase):
    class Config:
        orm_mode = True
