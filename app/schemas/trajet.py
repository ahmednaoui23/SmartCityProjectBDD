from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

"""
Pydantic schemas for Trajet.

- TrajetCreate: champs requis pour créer un trajet (origine, destination obligatoires).
- TrajetUpdate: champs optionnels pour mise à jour partielle.
- TrajetOut: schéma de sortie (orm_mode=True pour permettre la sérialisation d'objets SQLAlchemy).
"""

class TrajetBase(BaseModel):
    origine: Optional[str] = None
    destination: Optional[str] = None
    distance_km: Optional[Decimal] = Field(None, ge=0, description="Distance en kilomètres (>= 0)")
    duree_minutes: Optional[int] = Field(None, ge=0, description="Durée en minutes (>= 0)")
    co2_economie: Optional[Decimal] = Field(None, ge=0, description="Économie de CO2 estimée (kg ou unité convenue)")
    date_heure: Optional[datetime] = None
    plaque: Optional[str] = None  # référence à VEHICULE.plaque

class TrajetCreate(TrajetBase):
    origine: str
    destination: str

class TrajetUpdate(TrajetBase):
    pass

class TrajetOut(TrajetBase):

    class Config:
        model_config = {
            "from_attributes": True
        }