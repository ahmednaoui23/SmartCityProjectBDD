from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import mesure as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.MesureOut)
def create_mesure(payload: sch.MesureCreate, db: Session = Depends(get_db)):
    # validate capteur exist
    cap = db.query(models.Capteur).filter(models.Capteur.uuid_capteur == payload.uuid_capteur).first()
    if not cap:
        raise HTTPException(status_code=400, detail="Capteur not found")
    obj = models.Mesure(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[sch.MesureOut])
def list_mesures(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Mesure).order_by(models.Mesure.ts.desc()).limit(limit).all()