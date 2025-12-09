from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import vehicule as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.VehiculeOut)
def create_vehicule(payload: sch.VehiculeCreate, db: Session = Depends(get_db)):
    obj = models.Vehicule(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj