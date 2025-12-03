from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConsultationCreate(BaseModel):
    titre: Optional[str]
    date_consultation: Optional[datetime]
    theme: Optional[str]

class ConsultationOut(ConsultationCreate):
    class Config:
        model_config = {
            "from_attributes": True
        }