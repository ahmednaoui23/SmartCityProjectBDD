from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import vehicule as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.TrajetOut)
def create_trajet(payload: sch.TrajetCreate, db: Session = Depends(get_db)):
    if payload.plaque:
        v = db.query(models.Vehicule).filter(models.Vehicule.plaque == payload.plaque).first()
        if not v:
            raise HTTPException(status_code=400, detail="Vehicule not found")
    obj = models.Trajet(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/top")
def top_trajets(limit: int = 20, db: Session = Depends(get_db)):
    q = (
        db.query(
            models.Trajet.id_trajet,
            models.Trajet.origine,
            models.Trajet.destination,
            models.Trajet.co2_economie,
        )
        .filter(models.Trajet.co2_economie.isnot(None))
        .order_by(models.Trajet.co2_economie.desc())
        .limit(limit)
    )
    rows = q.all()
    out = []
    for r in rows:
        out.append({
            "id_trajet": r[0],
            "origine": r[1],
            "destination": r[2],
            "co2_economie": float(r[3]) if r[3] is not None else None
        })
    return out