from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import intervention as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.InterventionOut)
def create_intervention(payload: sch.InterventionCreate, db: Session = Depends(get_db)):
    obj = models.Intervention(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[sch.InterventionOut])
def list_interventions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Intervention).order_by(models.Intervention.date_heure.desc()).offset(skip).limit(limit).all()

@router.post("/{id_intervention}/close", response_model=sch.InterventionOut)
def close_intervention(id_intervention: int, db: Session = Depends(get_db)):
    inter = db.query(models.Intervention).filter(models.Intervention.id_intervention == id_intervention).first()
    if not inter:
        raise HTTPException(status_code=404, detail="Intervention not found")

    n = db.query(models.Realiser).filter(models.Realiser.id_intervention == id_intervention).count()
    if n < 2:
        raise HTTPException(status_code=400, detail="Intervention must have at least 2 technicians before closing")

    inter.ia_valide = True
    db.add(inter)
    db.commit()
    db.refresh(inter)
    return inter