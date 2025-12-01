from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import vehicule as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.TrajetOut)
def create_trajet(payload: sch.TrajetCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.create_trajet(db, payload)
        return obj
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/top")
def top_trajets(limit: int = 20, db: Session = Depends(get_db)):
    rows = crud.top_trajets(db, limit)
    return [{"id_trajet": r[0], "origine": r[1], "destination": r[2], "co2_economie": float(r[3] or 0)} for r in rows]