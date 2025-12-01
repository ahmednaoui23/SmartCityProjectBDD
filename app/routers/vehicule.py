from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import vehicule as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.VehiculeOut)
def create_vehicule(payload: sch.VehiculeCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_vehicule(db, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))