from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import realiser as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.RealiserCreate)
def add_realiser(payload: sch.RealiserCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.add_realiser(db, payload)
        return {"id_intervention": obj.id_intervention, "id_technicien": obj.id_technicien, "role": obj.role}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/")
def remove_realiser(id_intervention: int, id_technicien: int, db: Session = Depends(get_db)):
    ok = crud.remove_realiser(db, id_intervention, id_technicien)
    if not ok:
        raise HTTPException(status_code=404, detail="Realiser entry not found")
    return {"deleted": True}