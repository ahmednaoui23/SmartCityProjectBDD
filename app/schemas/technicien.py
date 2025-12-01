from pydantic import BaseModel
from typing import Optional

class TechnicienCreate(BaseModel):
    nom: str
    telephone: Optional[str]
    certification: Optional[str]

class TechnicienOut(TechnicienCreate):
    id_technicien: int
    class Config:
        model_config = {
            "from_attributes": True
        }