from pydantic import BaseModel

class RealiserCreate(BaseModel):
    id_intervention: int
    id_technicien: int
    role: str