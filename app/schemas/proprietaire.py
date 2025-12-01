from pydantic import BaseModel
from typing import Optional

class ProprietaireCreate(BaseModel):
    nom: str
    adresse: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    type_proprietaire: Optional[str]

class ProprietaireOut(ProprietaireCreate):
    id_proprietaire: int
    class Config:
        model_config = {
            "from_attributes": True
        }