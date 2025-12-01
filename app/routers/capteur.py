from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas import capteur as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.CapteurOut)
def create(cap: sch.CapteurCreate, db: Session = Depends(get_db)):
    return crud.create_capteur(db, cap)

@router.get("/", response_model=list[sch.CapteurOut])
def list_capteurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_capteurs(db, skip, limit)

@router.get("/{uuid}", response_model=sch.CapteurOut)
def get_cap(uuid: UUID, db: Session = Depends(get_db)):
    obj = crud.get_capteur(db, uuid)
    if not obj:
        raise HTTPException(status_code=404, detail="Capteur not found")
    return obj

@router.put("/{uuid}", response_model=sch.CapteurOut)
def update(uuid: UUID, payload: sch.CapteurCreate, db: Session = Depends(get_db)):
    obj = crud.update_capteur(db, uuid, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Capteur not found")
    return obj

@router.delete("/{uuid}")
def delete(uuid: UUID, db: Session = Depends(get_db)):
    ok = crud.delete_capteur(db, uuid)
    if not ok:
        raise HTTPException(status_code=404, detail="Capteur not found")
    return {"deleted": True}