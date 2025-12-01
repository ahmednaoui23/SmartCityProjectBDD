from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import technicien as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.TechnicienOut)
def create_technicien(payload: sch.TechnicienCreate, db: Session = Depends(get_db)):
    return crud.create_technicien(db, payload)

@router.get("/", response_model=list[sch.TechnicienOut])
def list_techniciens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_techniciens(db, skip, limit)