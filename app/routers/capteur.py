from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas import capteur as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.CapteurOut)
def create(cap: sch.CapteurCreate, db: Session = Depends(get_db)):
    obj = models.Capteur(**cap.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[sch.CapteurOut])
def list_capteurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Capteur).offset(skip).limit(limit).all()

@router.get("/{uuid}", response_model=sch.CapteurOut)
def get_cap(uuid: UUID, db: Session = Depends(get_db)):
    obj = db.query(models.Capteur).filter(models.Capteur.uuid_capteur == uuid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Capteur not found")
    return obj

@router.put("/{uuid}", response_model=sch.CapteurOut)
def update(uuid: UUID, payload: sch.CapteurCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Capteur).filter(models.Capteur.uuid_capteur == uuid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Capteur not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{uuid}")
def delete(uuid: UUID, db: Session = Depends(get_db)):
    obj = db.query(models.Capteur).filter(models.Capteur.uuid_capteur == uuid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Capteur not found")
    db.delete(obj)
    db.commit()
    return {"deleted": True}