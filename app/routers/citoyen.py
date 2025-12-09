from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import citoyen as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.CitoyenOut)
def create_citoyen(payload: sch.CitoyenCreate, db: Session = Depends(get_db)):
    obj = models.Citoyen(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[sch.CitoyenOut])
def list_citoyens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Citoyen).offset(skip).limit(limit).all()