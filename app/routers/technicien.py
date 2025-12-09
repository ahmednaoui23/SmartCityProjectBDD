from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import technicien as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.TechnicienOut)
def create_technicien(payload: sch.TechnicienCreate, db: Session = Depends(get_db)):
    obj = models.Technicien(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[sch.TechnicienOut])
def list_techniciens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Technicien).offset(skip).limit(limit).all()