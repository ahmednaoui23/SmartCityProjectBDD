from pydantic import BaseModel, EmailStr
from typing import Optional

class ProprietaireBase(BaseModel):
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: EmailStr
    type_proprietaire: Optional[str] = None

class ProprietaireCreate(ProprietaireBase):
    pass

class ProprietaireOut(ProprietaireBase):

    class Config:
        orm_mode = True