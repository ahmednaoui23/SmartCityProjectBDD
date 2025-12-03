from pydantic import BaseModel
from typing import Optional

class TechnicienCreate(BaseModel):
    nom: str
    telephone: Optional[str]
    certification: Optional[str]

class TechnicienOut(TechnicienCreate):
    class Config:
        model_config = {
            "from_attributes": True
        }