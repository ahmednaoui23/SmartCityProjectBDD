from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import realiser as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.RealiserCreate)
def add_realiser(payload: sch.RealiserCreate, db: Session = Depends(get_db)):
    # validate existence
    inter = db.query(models.Intervention).filter(models.Intervention.id_intervention == payload.id_intervention).first()
    tech = db.query(models.Technicien).filter(models.Technicien.id_technicien == payload.id_technicien).first()
    if not inter or not tech:
        raise HTTPException(status_code=400, detail="Intervention or Technicien not found")
    existing = db.query(models.Realiser).filter(
        models.Realiser.id_intervention == payload.id_intervention,
        models.Realiser.id_technicien == payload.id_technicien
    ).first()
    if existing:
        return existing
    obj = models.Realiser(id_intervention=payload.id_intervention, id_technicien=payload.id_technicien, role=payload.role)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/")
def remove_realiser(id_intervention: int, id_technicien: int, db: Session = Depends(get_db)):
    obj = db.query(models.Realiser).filter(
        models.Realiser.id_intervention == id_intervention,
        models.Realiser.id_technicien == id_technicien
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Realiser entry not found")
    db.delete(obj)
    db.commit()
    return {"deleted": True}